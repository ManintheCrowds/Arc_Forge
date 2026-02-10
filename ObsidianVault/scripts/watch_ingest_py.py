# PURPOSE: Event-driven PDF ingestion watcher using watchdog.
# DEPENDENCIES: watchdog library, ingest_pdfs.py, ingest_config.json.
# MODIFICATION NOTES: Replaces polling-based watcher with file system event monitoring.

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from queue import Queue
from threading import Event, Thread
from typing import Dict, Optional

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    # Create stub classes for graceful degradation
    class FileSystemEventHandler:
        pass
    class Observer:
        def __init__(self, *args, **kwargs):
            pass
        def schedule(self, *args, **kwargs):
            pass
        def start(self):
            pass
        def stop(self):
            pass
        def join(self, *args, **kwargs):
            pass
    # Don't exit on import - allow graceful degradation for testing
    if __name__ == "__main__":
        print("ERROR: watchdog library not installed. Install with: pip install watchdog", file=sys.stderr)
        sys.exit(1)

from utils import get_config_path, load_config, validate_vault_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


# PURPOSE: Handle file system events for PDF files.
# DEPENDENCIES: watchdog FileSystemEventHandler.
# MODIFICATION NOTES: Queues PDF files for processing with debouncing.
class PdfEventHandler(FileSystemEventHandler):
    def __init__(self, pdf_queue: Queue, pdf_root: Path, debounce_seconds: float = 2.0):
        super().__init__()
        self.pdf_queue = pdf_queue
        self.pdf_root = pdf_root.resolve()
        self.debounce_seconds = debounce_seconds
        self.pending_pdfs: Dict[Path, float] = {}
        self.last_process_time = 0.0

    def on_created(self, event):
        if event.is_directory:
            return
        self._handle_pdf_event(event.src_path)

    def on_modified(self, event):
        if event.is_directory:
            return
        self._handle_pdf_event(event.src_path)

    def _handle_pdf_event(self, file_path: str):
        """Handle PDF file creation or modification with debouncing."""
        try:
            pdf_path = Path(file_path).resolve()
            
            # Validate path is within PDF root
            try:
                pdf_path.relative_to(self.pdf_root)
            except ValueError:
                # File not in PDF root, ignore
                return
            
            # Only process PDF files
            if pdf_path.suffix.lower() != ".pdf":
                return
            
            # Validate path is within vault (security check)
            # Note: pdf_root should already be validated in config
            
            # Add to pending queue with timestamp for debouncing
            current_time = time.time()
            self.pending_pdfs[pdf_path] = current_time
            
            logger.debug(f"PDF event detected: {pdf_path.name} (pending debounce)")
            
        except Exception as e:
            logger.warning(f"Error handling PDF event for {file_path}: {e}")

    def process_pending(self):
        """Process pending PDFs after debounce period."""
        current_time = time.time()
        
        # Filter PDFs that have passed debounce period
        ready_pdfs = [
            pdf_path
            for pdf_path, event_time in self.pending_pdfs.items()
            if current_time - event_time >= self.debounce_seconds
        ]
        
        # Remove processed PDFs from pending
        for pdf_path in ready_pdfs:
            if pdf_path in self.pending_pdfs:
                del self.pending_pdfs[pdf_path]
        
        # Queue ready PDFs for processing
        for pdf_path in ready_pdfs:
            if pdf_path.exists():
                try:
                    self.pdf_queue.put(pdf_path, timeout=5)
                    logger.info(f"Queued PDF for processing: {pdf_path.name}")
                except Exception as e:
                    logger.warning(f"Failed to queue PDF {pdf_path.name}: {e}")


# PURPOSE: Process queued PDFs by calling ingestion script.
# DEPENDENCIES: ingest_pdfs.py script, config.
# MODIFICATION NOTES: Runs ingestion for queued PDFs with rate limiting.
class PdfProcessor(Thread):
    def __init__(
        self,
        pdf_queue: Queue,
        ingest_script: Path,
        config_path: Path,
        process_interval: float = 5.0,
        stop_event: Optional[Event] = None,
    ):
        super().__init__(daemon=True)
        self.pdf_queue = pdf_queue
        self.ingest_script = ingest_script
        self.config_path = config_path
        self.process_interval = process_interval
        self.stop_event = stop_event or Event()
        self.processing = False

    def run(self):
        """Process queued PDFs periodically."""
        logger.info("PDF processor thread started")
        
        while not self.stop_event.is_set():
            try:
                # Collect all queued PDFs
                queued_pdfs = []
                while not self.pdf_queue.empty():
                    try:
                        pdf_path = self.pdf_queue.get(timeout=0.1)
                        queued_pdfs.append(pdf_path)
                    except:
                        break
                
                if queued_pdfs:
                    logger.info(f"Processing {len(queued_pdfs)} queued PDF(s)")
                    self._process_pdfs(queued_pdfs)
                
                # Wait for next processing cycle
                self.stop_event.wait(self.process_interval)
                
            except Exception as e:
                logger.error(f"Error in PDF processor thread: {e}", exc_info=True)
                self.stop_event.wait(self.process_interval)
        
        logger.info("PDF processor thread stopped")

    def _process_pdfs(self, pdf_paths: list[Path]):
        """Run ingestion script for PDFs."""
        if self.processing:
            logger.warning("Processing already in progress, skipping batch")
            return
        
        self.processing = True
        try:
            # Run ingestion script (it will process all PDFs in directory)
            # For now, we trigger full ingestion; could be optimized to process specific PDFs
            cmd = [
                sys.executable,
                str(self.ingest_script),
                "--config",
                str(self.config_path),
            ]
            
            logger.info(f"Executing ingestion: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully processed {len(pdf_paths)} PDF(s)")
            else:
                logger.error(
                    f"Ingestion failed (exit code {result.returncode}): "
                    f"{result.stderr[:500]}"
                )
                
        except subprocess.TimeoutExpired:
            logger.error("Ingestion timed out after 10 minutes")
        except Exception as e:
            logger.error(f"Error running ingestion: {e}", exc_info=True)
        finally:
            self.processing = False


# PURPOSE: Main watcher service that monitors PDF directory.
# DEPENDENCIES: watchdog Observer, config.
# MODIFICATION NOTES: Sets up file system monitoring and processing threads.
def run_watcher(config: Dict[str, object], debounce_seconds: float = 2.0, process_interval: float = 5.0) -> None:
    """
    Run event-driven PDF watcher service.
    
    Args:
        config: Configuration dictionary.
        debounce_seconds: Seconds to wait before processing a PDF after event.
        process_interval: Seconds between processing batches.
    """
    vault_root = Path(str(config["vault_root"])).resolve()
    pdf_root = get_config_path(vault_root, config, "pdf_root")
    
    # Validate PDF root exists
    if not pdf_root.exists():
        logger.error(f"PDF root directory does not exist: {pdf_root}")
        sys.exit(1)
    
    logger.info(f"Starting PDF watcher for: {pdf_root}")
    logger.info(f"Debounce: {debounce_seconds}s, Process interval: {process_interval}s")
    
    # Setup paths
    script_dir = Path(__file__).parent
    ingest_script = script_dir / "ingest_pdfs.py"
    config_path = script_dir / "ingest_config.json"
    
    if not ingest_script.exists():
        logger.error(f"Ingestion script not found: {ingest_script}")
        sys.exit(1)
    
    # Create queue and event handler
    pdf_queue: Queue[Path] = Queue()
    event_handler = PdfEventHandler(pdf_queue, pdf_root, debounce_seconds=debounce_seconds)
    
    # Create observer
    observer = Observer()
    observer.schedule(event_handler, str(pdf_root), recursive=True)
    
    # Create processor thread
    stop_event = Event()
    processor = PdfProcessor(
        pdf_queue,
        ingest_script,
        config_path,
        process_interval=process_interval,
        stop_event=stop_event,
    )
    
    # Start observer and processor
    observer.start()
    processor.start()
    
    logger.info("PDF watcher started. Press Ctrl+C to stop.")
    
    try:
        # Periodically process pending PDFs (for debouncing)
        while True:
            time.sleep(1)
            event_handler.process_pending()
    except KeyboardInterrupt:
        logger.info("Stopping PDF watcher...")
        stop_event.set()
        observer.stop()
        observer.join(timeout=5)
        processor.join(timeout=10)
        logger.info("PDF watcher stopped")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Event-driven PDF ingestion watcher.")
    parser.add_argument(
        "--config",
        default="ingest_config.json",
        help="Path to ingestion config JSON.",
    )
    parser.add_argument(
        "--debounce",
        type=float,
        default=2.0,
        help="Debounce time in seconds before processing PDF (default: 2.0).",
    )
    parser.add_argument(
        "--process-interval",
        type=float,
        default=5.0,
        help="Interval between processing batches in seconds (default: 5.0).",
    )
    return parser.parse_args()


def main() -> None:
    if not WATCHDOG_AVAILABLE:
        sys.exit(1)
    
    args = parse_args()
    config_path = Path(args.config)
    
    if not config_path.is_absolute():
        config_path = Path(__file__).parent / config_path
    
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    
    try:
        config = load_config(config_path)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    run_watcher(
        config,
        debounce_seconds=args.debounce,
        process_interval=args.process_interval,
    )


if __name__ == "__main__":
    main()
