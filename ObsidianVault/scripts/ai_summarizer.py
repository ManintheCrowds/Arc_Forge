# PURPOSE: AI-powered document summarization (Phase 2).
# DEPENDENCIES: openai, anthropic, or ollama.
# MODIFICATION NOTES: Phase 2 - Complete implementation. AI security P0: credential vault for API keys.

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple

logger = logging.getLogger(__name__)

# #region agent log
DEBUG_LOG_PATH = Path("d:\\CodeRepositories\\.cursor\\debug.log")
def _debug_log(location: str, message: str, data: dict, hypothesis_id: str = "C"):
    try:
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": hypothesis_id,
                "location": location,
                "message": message,
                "data": data,
                "timestamp": int(time.time() * 1000)
            }) + "\n")
    except: pass
# #endregion

# Try to import LLM dependencies
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


# Cost calculation tables (per 1K tokens, approximate as of 2024)
OPENAI_COSTS = {
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
}

ANTHROPIC_COSTS = {
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
}


def _calculate_openai_cost(model: str, total_tokens: Optional[int]) -> Optional[float]:
    """Calculate cost for OpenAI API call."""
    if not total_tokens:
        return None
    
    costs = OPENAI_COSTS.get(model, OPENAI_COSTS.get("gpt-3.5-turbo"))
    # Approximate 50/50 input/output split
    input_cost = (total_tokens * 0.5 / 1000) * costs["input"]
    output_cost = (total_tokens * 0.5 / 1000) * costs["output"]
    return input_cost + output_cost


def _calculate_anthropic_cost(model: str, total_tokens: Optional[int]) -> Optional[float]:
    """Calculate cost for Anthropic API call."""
    if not total_tokens:
        return None
    
    costs = ANTHROPIC_COSTS.get(model, ANTHROPIC_COSTS.get("claude-3-sonnet"))
    # Approximate 50/50 input/output split
    input_cost = (total_tokens * 0.5 / 1000) * costs["input"]
    output_cost = (total_tokens * 0.5 / 1000) * costs["output"]
    return input_cost + output_cost


def _get_provider_client(provider: str, api_key: Optional[str] = None):
    """
    Get provider client instance.
    
    Args:
        provider: Provider name ("openai", "anthropic", "ollama")
        api_key: Optional API key
        
    Returns:
        Client instance or None
    """
    if provider == "openai" and OPENAI_AVAILABLE:
        return openai.OpenAI(api_key=api_key) if api_key else openai.OpenAI()
    elif provider == "anthropic" and ANTHROPIC_AVAILABLE:
        return anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
    elif provider == "ollama" and OLLAMA_AVAILABLE:
        return None  # Ollama doesn't use a client object
    return None


def _call_openai_api(
    prompt: str,
    model: str,
    api_key: Optional[str],
    max_tokens: int,
    temperature: float,
    max_retries: int = 3,
    retry_delay: float = 1.0,
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Call OpenAI API with retry logic and error handling.
    
    Args:
        prompt: Prompt text
        model: Model name
        api_key: API key (None to use environment variable)
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature
        max_retries: Maximum retry attempts
        retry_delay: Initial delay between retries (exponential backoff)
        
    Returns:
        Tuple of (summary_text, metadata_dict) where metadata includes tokens_used, cost, etc.
    """
    if not OPENAI_AVAILABLE:
        logger.error("OpenAI library not available")
        return None, None

    try:
        from audit_ai import log_ai_action
        log_ai_action(prompt[:500], model, "summarize_openai")
    except ImportError:
        pass

    if api_key is None:
        try:
            from credential_vault import get_secret
            api_key = get_secret("OPENAI_API_KEY")
        except ImportError:
            api_key = os.environ.get("OPENAI_API_KEY")

    if api_key:
        try:
            from cloud_ai_consent import has_cloud_ai_consent
            if not has_cloud_ai_consent():
                logger.error("Cloud AI (OpenAI) consent required. Set CLOUD_AI_CONSENT=1 or create ~/.config/arc_forge/cloud_ai_consent")
                return None, None
        except ImportError:
            pass

    client = openai.OpenAI(api_key=api_key) if api_key else openai.OpenAI()
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise, informative summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            summary = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None
            
            # Calculate cost (approximate, varies by model)
            cost = _calculate_openai_cost(model, tokens_used) if tokens_used else None
            
            metadata = {
                "provider": "openai",
                "model": model,
                "tokens_used": tokens_used,
                "cost": cost,
                "timestamp": datetime.now().isoformat(),
            }
            
            if summary:
                logger.debug(f"OpenAI summary generated ({len(summary)} chars, {tokens_used} tokens)")
            return summary, metadata
            
        except openai.RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                logger.warning(f"OpenAI rate limit hit, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"OpenAI rate limit error after {max_retries} attempts: {e}")
                return None, None
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return None, None
        except Exception as e:
            logger.error(f"Unexpected OpenAI error: {e}")
            return None, None
    
    return None, None


def _call_anthropic_api(
    prompt: str,
    model: str,
    api_key: Optional[str],
    max_tokens: int,
    temperature: float,
    max_retries: int = 3,
    retry_delay: float = 1.0,
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Call Anthropic (Claude) API with retry logic and error handling.
    
    Args:
        prompt: Prompt text
        model: Model name
        api_key: API key (None to use environment variable)
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature
        max_retries: Maximum retry attempts
        retry_delay: Initial delay between retries (exponential backoff)
        
    Returns:
        Tuple of (summary_text, metadata_dict)
    """
    if not ANTHROPIC_AVAILABLE:
        logger.error("Anthropic library not available")
        return None, None

    try:
        from audit_ai import log_ai_action
        log_ai_action(prompt[:500], model, "summarize_anthropic")
    except ImportError:
        pass

    if api_key is None:
        try:
            from credential_vault import get_secret
            api_key = get_secret("ANTHROPIC_API_KEY")
        except ImportError:
            api_key = os.environ.get("ANTHROPIC_API_KEY")

    if api_key:
        try:
            from cloud_ai_consent import has_cloud_ai_consent
            if not has_cloud_ai_consent():
                logger.error("Cloud AI (Anthropic) consent required. Set CLOUD_AI_CONSENT=1 or create ~/.config/arc_forge/cloud_ai_consent")
                return None, None
        except ImportError:
            pass

    client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
    
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system="You are a helpful assistant that creates concise, informative summaries.",
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            
            summary = response.content[0].text if response.content else None
            tokens_used = response.usage.input_tokens + response.usage.output_tokens if response.usage else None
            
            # Calculate cost (approximate, varies by model)
            cost = _calculate_anthropic_cost(model, tokens_used) if tokens_used else None
            
            metadata = {
                "provider": "anthropic",
                "model": model,
                "tokens_used": tokens_used,
                "cost": cost,
                "timestamp": datetime.now().isoformat(),
            }
            
            if summary:
                logger.debug(f"Anthropic summary generated ({len(summary)} chars, {tokens_used} tokens)")
            return summary, metadata
            
        except anthropic.RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                logger.warning(f"Anthropic rate limit hit, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"Anthropic rate limit error after {max_retries} attempts: {e}")
                return None, None
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {e}")
            return None, None
        except Exception as e:
            logger.error(f"Unexpected Anthropic error: {e}")
            return None, None
    
    return None, None


def _call_ollama_api(
    prompt: str,
    model: str,
    max_tokens: int,
    temperature: float,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    endpoint: Optional[str] = None,
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Call Ollama local API with retry logic and error handling.
    
    Args:
        prompt: Prompt text
        model: Model name
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature
        max_retries: Maximum retry attempts
        retry_delay: Initial delay between retries (exponential backoff)
        endpoint: Optional Ollama endpoint URL (default: localhost:11434 or OLLAMA_HOST env var)
        
    Returns:
        Tuple of (summary_text, metadata_dict)
    """
    if not OLLAMA_AVAILABLE:
        logger.error("Ollama library not available")
        return None, None

    try:
        from audit_ai import log_ai_action
        log_ai_action(prompt[:500], model, "summarize_ollama")
    except ImportError:
        pass

    # Get endpoint from parameter, environment variable, or default
    if endpoint is None:
        endpoint = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    # Configure Ollama client with endpoint if supported
    # Note: ollama library uses OLLAMA_HOST env var or defaults to localhost:11434
    # We'll set it temporarily if a custom endpoint is provided
    original_host = os.environ.get("OLLAMA_HOST")
    try:
        if endpoint and endpoint != "http://localhost:11434":
            # Extract host from endpoint (remove http:// or https://)
            host = endpoint.replace("http://", "").replace("https://", "")
            os.environ["OLLAMA_HOST"] = host
            logger.debug(f"Using Ollama endpoint: {host}")
    except Exception as e:
        logger.warning(f"Failed to set OLLAMA_HOST: {e}")
    
    for attempt in range(max_retries):
        try:
            response = ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise, informative summaries."},
                    {"role": "user", "content": prompt}
                ],
                options={
                    "num_predict": max_tokens,
                    "temperature": temperature,
                }
            )
            
            summary = response["message"]["content"] if response.get("message") else None
            
            # Extract token counts from Ollama response if available
            # Ollama provides: prompt_eval_count (input tokens), eval_count (output tokens)
            prompt_tokens = response.get("prompt_eval_count")
            output_tokens = response.get("eval_count")
            
            if prompt_tokens is not None and output_tokens is not None:
                tokens_used = prompt_tokens + output_tokens
                logger.debug(f"Ollama token count from API: {tokens_used} (input: {prompt_tokens}, output: {output_tokens})")
            else:
                # Fallback to estimation if metadata not available
                tokens_used = len(summary) // 4 if summary else None
                logger.debug(f"Ollama token count estimated: {tokens_used}")
            
            metadata = {
                "provider": "ollama",
                "model": model,
                "tokens_used": tokens_used,
                "prompt_tokens": prompt_tokens,
                "output_tokens": output_tokens,
                "cost": 0.0,  # Local, no cost
                "timestamp": datetime.now().isoformat(),
            }
            
            if summary:
                logger.debug(f"Ollama summary generated ({len(summary)} chars, {tokens_used} tokens)")
            return summary, metadata
            
        except ConnectionError as e:
            error_msg = str(e).lower()
            if "connection" in error_msg or "refused" in error_msg or "unreachable" in error_msg:
                logger.error(f"Ollama connection error: Ollama may not be running at {endpoint}. Please start Ollama service.")
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                logger.warning(f"Ollama connection error, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"Ollama connection error after {max_retries} attempts: {e}")
                return None, None
        except Exception as e:
            error_msg = str(e).lower()
            if "model" in error_msg and ("not found" in error_msg or "does not exist" in error_msg):
                logger.error(f"Ollama model '{model}' not found. Please install it with: ollama pull {model}")
            elif "timeout" in error_msg:
                logger.warning(f"Ollama request timeout: {e}")
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                logger.warning(f"Ollama error, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"Ollama API error after {max_retries} attempts: {e}")
                return None, None
        finally:
            # Restore original OLLAMA_HOST if we changed it
            if original_host is not None:
                os.environ["OLLAMA_HOST"] = original_host
            elif "OLLAMA_HOST" in os.environ and endpoint and endpoint != "http://localhost:11434":
                # Only remove if we set it
                del os.environ["OLLAMA_HOST"]
    
    return None, None


def chunk_text(text: str, max_chunk_size: int = 12000, overlap: int = 200) -> List[str]:
    """
    Split text into chunks for LLM processing, preserving sentence boundaries with overlap.
    
    Args:
        text: Text to chunk.
        max_chunk_size: Maximum characters per chunk (default: 12000).
        overlap: Overlap between chunks for context (default: 200).
        
    Returns:
        List of text chunks.
    """
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    current_chunk = ""
    for sentence in sentences:
        # If adding this sentence would exceed max size, save current chunk
        if len(current_chunk) + len(sentence) + 1 > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Start new chunk with overlap from previous chunk
            if overlap > 0:
                # Get last N characters for overlap
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                # Find last sentence boundary in overlap
                overlap_sentences = re.split(r'(?<=[.!?])\s+', overlap_text)
                if len(overlap_sentences) > 1:
                    current_chunk = " ".join(overlap_sentences[-2:]) + " " + sentence
                else:
                    current_chunk = sentence
            else:
                current_chunk = sentence
        else:
            current_chunk += (" " + sentence if current_chunk else sentence)
    
    # Add remaining chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks if chunks else [text]


# PURPOSE: Split text on section boundaries first; fall back to sentence chunking for large sections.
# DEPENDENCIES: chunk_text.
# MODIFICATION NOTES: Phase 2 structural chunking per pdf_chunking_rag_strategy plan.
def chunk_by_sections(
    text: str,
    max_chunk_size: int = 8000,
    overlap: int = 200,
) -> List[str]:
    """
    Split text on section boundaries (headings, Chapter/Section markers), then by sentences
    for sections that exceed max_chunk_size.

    Args:
        text: Text to chunk.
        max_chunk_size: Maximum characters per chunk.
        overlap: Overlap between chunks when falling back to sentence chunking.

    Returns:
        List of text chunks.
    """
    if len(text) <= max_chunk_size:
        return [text]

    # Conservative: markdown headers, Chapter N, Section N
    section_pattern = re.compile(r'\n(?=#{1,3}\s|Chapter\s|Section\s)', re.MULTILINE)
    raw_sections = section_pattern.split(text)

    chunks: List[str] = []
    for sec in raw_sections:
        sec = sec.strip()
        if not sec:
            continue
        if len(sec) <= max_chunk_size:
            chunks.append(sec)
        else:
            chunks.extend(chunk_text(sec, max_chunk_size=max_chunk_size, overlap=overlap))

    return chunks if chunks else [text]


def get_cached_summary(text_hash: str, cache_dir: Path) -> Optional[Tuple[str, Dict]]:
    """
    Get cached summary if available.
    
    Args:
        text_hash: Hash of text to summarize.
        cache_dir: Directory for summary cache.
        
    Returns:
        Tuple of (summary_text, metadata_dict) or None if not found.
    """
    try:
        # Try JSON cache first (with metadata)
        json_cache_path = cache_dir / f"{text_hash}.json"
        if json_cache_path.exists():
            cache_data = json.loads(json_cache_path.read_text(encoding="utf-8"))
            summary = cache_data.get("summary", "")
            metadata = cache_data.get("metadata", {})
            logger.debug(f"Retrieved cached summary (JSON) for hash {text_hash[:8]}")
            return summary, metadata
        
        # Fallback to text cache (legacy)
        txt_cache_path = cache_dir / f"{text_hash}.txt"
        if txt_cache_path.exists():
            summary = txt_cache_path.read_text(encoding="utf-8")
            logger.debug(f"Retrieved cached summary (TXT) for hash {text_hash[:8]}")
            return summary, {}
    except Exception as e:
        logger.warning(f"Failed to read summary cache: {e}")
    return None


def save_summary_cache(text_hash: str, summary: str, cache_dir: Path, metadata: Optional[Dict] = None) -> None:
    """
    Save summary to cache with metadata.
    
    Args:
        text_hash: Hash of text.
        summary: Summary text.
        cache_dir: Directory for summary cache.
        metadata: Optional metadata dictionary (tokens, cost, etc.).
    """
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON with metadata
        cache_data = {
            "text_hash": text_hash,
            "summary": summary,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
        }
        json_cache_path = cache_dir / f"{text_hash}.json"
        json_cache_path.write_text(json.dumps(cache_data, indent=2), encoding="utf-8")
        logger.debug(f"Saved summary cache (JSON) for hash {text_hash[:8]}")
        
        # Also save as text for backward compatibility
        txt_cache_path = cache_dir / f"{text_hash}.txt"
        txt_cache_path.write_text(summary, encoding="utf-8")
    except Exception as e:
        logger.warning(f"Failed to save summary cache: {e}")


def _get_rpg_prompt_template() -> str:
    """Get RPG-specific prompt template for summarization."""
    return """Summarize the following RPG document (Wrath & Glory, Warhammer 40k, or similar). 
Focus on:
- Key rules and mechanics
- Important NPCs, factions, and locations
- Notable items, equipment, or artifacts
- Campaign-relevant information

Provide a concise summary (2-3 paragraphs) that captures the essential information for a Game Master.

Document text:
{text}"""


def _get_generic_prompt_template() -> str:
    """Get generic prompt template for summarization."""
    return """Summarize the following document. Provide a concise summary (2-3 paragraphs) 
that captures the key points and essential information.

Document text:
{text}"""


def summarize_text(
    text: str,
    provider: str = "ollama",
    model: str = "llama2",
    api_key: Optional[str] = None,
    max_tokens: int = 500,
    temperature: float = 0.7,
    rpg_mode: bool = True,
    cache_dir: Optional[Path] = None,
    ollama_endpoint: Optional[str] = None,
) -> Optional[str]:
    """
    Generate summary of text using LLM with caching and cost tracking.
    
    Args:
        text: Text to summarize.
        provider: LLM provider ("openai", "anthropic", "ollama").
        model: Model name to use.
        api_key: API key for provider (None for Ollama or environment variable).
        max_tokens: Maximum tokens in summary.
        temperature: Sampling temperature.
        rpg_mode: Whether to use RPG-specific prompt template (default: True).
        cache_dir: Optional cache directory for summaries.
        ollama_endpoint: Optional Ollama endpoint URL (default: localhost:11434 or OLLAMA_HOST env var).
        
    Returns:
        Summary text or None if summarization fails.
    """
    if not text.strip():
        logger.warning("Empty text provided for summarization")
        return None
    
    # Check provider availability
    if provider == "openai" and not OPENAI_AVAILABLE:
        logger.error("OpenAI library not available")
        return None
    
    if provider == "anthropic" and not ANTHROPIC_AVAILABLE:
        logger.error("Anthropic library not available")
        return None
    
    if provider == "ollama" and not OLLAMA_AVAILABLE:
        logger.error("Ollama library not available")
        return None
    
    # Check cache if cache_dir provided
    if cache_dir:
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        cached = get_cached_summary(text_hash, cache_dir)
        if cached:
            summary, metadata = cached
            logger.info(f"Using cached summary (cost saved: ${metadata.get('cost', 0):.4f})")
            return summary
    
    try:
        # Chunk text if too long (estimate ~4 chars per token, leave room for prompt)
        max_text_tokens = 3000  # Leave room for prompt
        # #region agent log
        _debug_log("ai_summarizer.py:569", "Before chunking", {"text_length": len(text), "max_chunk_size": max_text_tokens * 4}, "C")
        # #endregion
        text_chunks = chunk_text(text, max_chunk_size=max_text_tokens * 4, overlap=200)
        # #region agent log
        _debug_log("ai_summarizer.py:572", "Chunking complete", {"num_chunks": len(text_chunks), "chunk_sizes": [len(c) for c in text_chunks[:5]]}, "C")
        # #endregion
        
        logger.info(f"Summarizing text with {provider}/{model} ({len(text_chunks)} chunk(s))")
        
        # Use RPG template if enabled, otherwise generic
        prompt_template = _get_rpg_prompt_template() if rpg_mode else _get_generic_prompt_template()
        
        summaries = []
        total_cost = 0.0
        total_tokens = 0
        
        for i, chunk in enumerate(text_chunks, 1):
            prompt = prompt_template.format(text=chunk)
            # #region agent log
            chunk_start = time.time()
            _debug_log("ai_summarizer.py:583", "Processing chunk", {"chunk_num": i, "total_chunks": len(text_chunks), "chunk_size": len(chunk), "provider": provider}, "C")
            # #endregion
            
            try:
                if provider == "openai":
                    # Only pass api_key for API-based providers
                    summary, metadata = _call_openai_api(prompt, model, api_key, max_tokens, temperature)
                elif provider == "anthropic":
                    # Only pass api_key for API-based providers
                    summary, metadata = _call_anthropic_api(prompt, model, api_key, max_tokens, temperature)
                elif provider == "ollama":
                    # Ollama doesn't need api_key, pass endpoint instead
                    summary, metadata = _call_ollama_api(prompt, model, max_tokens, temperature, endpoint=ollama_endpoint)
                else:
                    logger.error(f"Unknown provider: {provider}")
                    return None
                
                # #region agent log
                chunk_elapsed = time.time() - chunk_start
                _debug_log("ai_summarizer.py:600", "Chunk processed", {"chunk_num": i, "elapsed_seconds": chunk_elapsed, "summary_length": len(summary) if summary else 0}, "C")
                # #endregion
                
                if summary:
                    summaries.append(summary)
                    if metadata:
                        total_cost += metadata.get("cost", 0.0)
                        total_tokens += metadata.get("tokens_used", 0)
                    logger.debug(f"Generated summary for chunk {i}/{len(text_chunks)}")
                else:
                    logger.warning(f"Failed to generate summary for chunk {i}/{len(text_chunks)}")
            except Exception as e:
                # #region agent log
                _debug_log("ai_summarizer.py:610", "Chunk processing error", {"chunk_num": i, "error": str(e)}, "C")
                # #endregion
                logger.error(f"Error summarizing chunk {i}/{len(text_chunks)}: {e}")
                continue
        
        if not summaries:
            logger.warning("No summaries generated from any chunk")
            return None
        
        # Combine summaries if multiple chunks
        if len(summaries) > 1:
            combined = "\n\n".join(summaries)
            # Optionally summarize the combined summaries for very long documents
            if len(combined) > max_tokens * 4:
                logger.info("Summarizing combined summaries (document too long)")
                return summarize_text(
                    combined,
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    rpg_mode=rpg_mode,
                    cache_dir=cache_dir,
                    ollama_endpoint=ollama_endpoint,
                )
            final_summary = combined
        else:
            final_summary = summaries[0]
        
        # Save to cache if cache_dir provided
        if cache_dir and final_summary:
            metadata = {
                "provider": provider,
                "model": model,
                "tokens_used": total_tokens,
                "cost": total_cost,
                "chunks": len(text_chunks),
            }
            save_summary_cache(text_hash, final_summary, cache_dir, metadata)
            if total_cost > 0:
                logger.info(f"Summary generated (cost: ${total_cost:.4f}, tokens: {total_tokens})")
        
        return final_summary
        
    except Exception as e:
        logger.error(f"Summarization failed: {e}", exc_info=True)
        return None


# Legacy wrapper functions for backward compatibility
def _summarize_with_openai(
    prompt: str,
    model: str,
    api_key: Optional[str],
    max_tokens: int,
    temperature: float,
) -> Optional[str]:
    """Summarize using OpenAI API (legacy wrapper)."""
    summary, _ = _call_openai_api(prompt, model, api_key, max_tokens, temperature)
    return summary


def _summarize_with_anthropic(
    prompt: str,
    model: str,
    api_key: Optional[str],
    max_tokens: int,
    temperature: float,
) -> Optional[str]:
    """Summarize using Anthropic (Claude) API (legacy wrapper)."""
    summary, _ = _call_anthropic_api(prompt, model, api_key, max_tokens, temperature)
    return summary


def _summarize_with_ollama(
    prompt: str,
    model: str,
    max_tokens: int,
    temperature: float,
) -> Optional[str]:
    """Summarize using local Ollama (legacy wrapper)."""
    summary, _ = _call_ollama_api(prompt, model, max_tokens, temperature, endpoint=None)
    return summary


def check_ollama_health(endpoint: Optional[str] = None) -> bool:
    """
    Check if Ollama service is running and accessible.
    
    Args:
        endpoint: Optional Ollama endpoint URL (default: localhost:11434 or OLLAMA_HOST env var).
        
    Returns:
        True if Ollama is running and accessible, False otherwise.
    """
    if not OLLAMA_AVAILABLE:
        logger.debug("Ollama library not available")
        return False
    
    try:
        # Get endpoint from parameter, environment variable, or default
        if endpoint is None:
            endpoint = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        
        # Extract host from endpoint
        host = endpoint.replace("http://", "").replace("https://", "")
        original_host = os.environ.get("OLLAMA_HOST")
        
        try:
            if endpoint != "http://localhost:11434":
                os.environ["OLLAMA_HOST"] = host
        except Exception:
            pass
        
        # Try to list models as a health check
        # This is a lightweight operation that verifies Ollama is running
        try:
            models = ollama.list()
            # If we get a response (even empty list), Ollama is running
            logger.debug(f"Ollama health check passed at {endpoint}")
            return True
        except Exception as e:
            logger.debug(f"Ollama health check failed: {e}")
            return False
        finally:
            # Restore original OLLAMA_HOST if we changed it
            if original_host is not None:
                os.environ["OLLAMA_HOST"] = original_host
            elif "OLLAMA_HOST" in os.environ and endpoint != "http://localhost:11434":
                try:
                    del os.environ["OLLAMA_HOST"]
                except Exception:
                    pass
    except Exception as e:
        logger.debug(f"Ollama health check error: {e}")
        return False


def check_model_available(model_name: str, endpoint: Optional[str] = None) -> bool:
    """
    Check if a specific Ollama model is installed and available.
    
    Args:
        model_name: Name of the model to check (e.g., "llama2", "mistral").
        endpoint: Optional Ollama endpoint URL (default: localhost:11434 or OLLAMA_HOST env var).
        
    Returns:
        True if model is available, False otherwise.
    """
    if not OLLAMA_AVAILABLE:
        logger.debug("Ollama library not available")
        return False
    
    try:
        # Get endpoint from parameter, environment variable, or default
        if endpoint is None:
            endpoint = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        
        # Extract host from endpoint
        host = endpoint.replace("http://", "").replace("https://", "")
        original_host = os.environ.get("OLLAMA_HOST")
        
        try:
            if endpoint != "http://localhost:11434":
                os.environ["OLLAMA_HOST"] = host
        except Exception:
            pass
        
        try:
            # List all available models
            models_response = ollama.list()
            models = models_response.get("models", [])
            
            # Check if the requested model is in the list
            # Model names in Ollama can have tags (e.g., "llama2:latest")
            # So we check if the model_name matches or is a prefix
            for model in models:
                model_full_name = model.get("name", "")
                if model_name == model_full_name or model_full_name.startswith(f"{model_name}:"):
                    logger.debug(f"Model '{model_name}' is available")
                    return True
            
            logger.debug(f"Model '{model_name}' not found in available models")
            return False
        except Exception as e:
            logger.debug(f"Error checking model availability: {e}")
            return False
        finally:
            # Restore original OLLAMA_HOST if we changed it
            if original_host is not None:
                os.environ["OLLAMA_HOST"] = original_host
            elif "OLLAMA_HOST" in os.environ and endpoint != "http://localhost:11434":
                try:
                    del os.environ["OLLAMA_HOST"]
                except Exception:
                    pass
    except Exception as e:
        logger.debug(f"Model availability check error: {e}")
        return False
