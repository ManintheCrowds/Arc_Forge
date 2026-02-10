# PURPOSE: Workflow GUI package (Phase 3). Thin UI over storyboard_workflow.
# DEPENDENCIES: flask, scripts.storyboard_workflow (when run from ObsidianVault).
from .app import app

__all__ = ["app"]
