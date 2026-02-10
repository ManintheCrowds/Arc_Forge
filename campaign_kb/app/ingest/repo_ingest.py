# PURPOSE: Download and extract GitHub repositories for documentation ingest.
# DEPENDENCIES: httpx, zipfile, tempfile, pathlib, urllib.parse
# MODIFICATION NOTES: MVP GitHub repo ingestion helper.

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlparse
import zipfile

import httpx

from app.utils.text import normalize_text
from app.utils.files import list_text_files


@dataclass
class RepoDocument:
    # PURPOSE: Represent a document extracted from a repo.
    # DEPENDENCIES: dataclasses
    # MODIFICATION NOTES: MVP repo document container.

    title: str
    relative_path: str
    text: str


def _parse_github_repo(url: str) -> tuple[str, str] | None:
    # PURPOSE: Parse owner/repo from a GitHub URL.
    # DEPENDENCIES: urllib.parse
    # MODIFICATION NOTES: MVP parser for https://github.com/{owner}/{repo}.
    parsed = urlparse(url)
    if parsed.netloc.lower() != "github.com":
        return None
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        return None
    return parts[0], parts[1]


def _download_repo_zip(owner: str, repo: str, timeout_seconds: float) -> bytes:
    # PURPOSE: Download a GitHub repository zip archive.
    # DEPENDENCIES: httpx
    # MODIFICATION NOTES: Try main then master branches.
    candidates = [
        f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/main",
        f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/master",
    ]
    for url in candidates:
        response = httpx.get(url, timeout=timeout_seconds)
        if response.status_code == 200:
            return response.content
    raise ValueError(f"Unable to download repo {owner}/{repo} from GitHub.")


def extract_repo_documents(repo_url: str, timeout_seconds: float = 20.0) -> list[RepoDocument]:
    # PURPOSE: Extract readable docs from a GitHub repo archive.
    # DEPENDENCIES: httpx, zipfile, tempfile
    # MODIFICATION NOTES: MVP extraction for markdown/text/html docs.
    parsed = _parse_github_repo(repo_url)
    if not parsed:
        raise ValueError("Only GitHub repo URLs are supported for now.")
    owner, repo = parsed
    archive = _download_repo_zip(owner, repo, timeout_seconds=timeout_seconds)

    documents: list[RepoDocument] = []
    with TemporaryDirectory() as temp_dir:
        zip_path = Path(temp_dir) / f"{repo}.zip"
        zip_path.write_bytes(archive)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        root_candidates = list(Path(temp_dir).glob(f"{repo}-*"))
        repo_root = root_candidates[0] if root_candidates else Path(temp_dir)
        for doc_path in list_text_files(repo_root, recursive=True):
            try:
                raw_text = doc_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            normalized = normalize_text(raw_text)
            if not normalized:
                continue
            relative_path = str(doc_path.relative_to(repo_root))
            documents.append(
                RepoDocument(
                    title=doc_path.stem,
                    relative_path=relative_path,
                    text=normalized,
                )
            )
    return documents
