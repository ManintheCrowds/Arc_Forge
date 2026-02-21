# PURPOSE: Unit tests for AI summarizer functionality.
# DEPENDENCIES: pytest, ai_summarizer module.
# MODIFICATION NOTES: Tests summarization, chunking, caching, and error handling.

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import hashlib

from ai_summarizer import (
    summarize_text,
    chunk_text,
    chunk_by_sections,
    get_cached_summary,
    save_summary_cache,
    _call_openai_api,
    _call_anthropic_api,
    _call_ollama_api,
    _calculate_openai_cost,
    _calculate_anthropic_cost,
    _get_rpg_prompt_template,
    _get_generic_prompt_template,
    OPENAI_AVAILABLE,
    ANTHROPIC_AVAILABLE,
    OLLAMA_AVAILABLE,
)


class TestChunkText:
    """Tests for text chunking functionality."""
    
    def test_chunk_short_text(self):
        """Test that short text returns single chunk."""
        text = "This is a short text."
        chunks = chunk_text(text, max_chunk_size=1000)
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_chunk_long_text(self):
        """Test that long text is split into multiple chunks."""
        text = ". ".join([f"Sentence {i}" for i in range(100)])
        chunks = chunk_text(text, max_chunk_size=100)
        assert len(chunks) > 1
        assert all(len(chunk) <= 100 for chunk in chunks)
    
    def test_chunk_preserves_sentences(self):
        """Test that chunking preserves sentence boundaries."""
        text = "First sentence. Second sentence. Third sentence."
        chunks = chunk_text(text, max_chunk_size=30)
        # Should split at sentence boundaries
        assert any("First sentence" in chunk for chunk in chunks)
        assert any("Second sentence" in chunk for chunk in chunks)
    
    def test_chunk_with_overlap(self):
        """Test chunking with overlap (Phase 2)."""
        text = ". ".join([f"Sentence {i}" for i in range(20)])
        chunks = chunk_text(text, max_chunk_size=100, overlap=20)
        
        # Should have overlap between chunks
        assert len(chunks) > 1
        # Overlap uses sentence boundaries: last sentence(s) of chunk 0 should appear in chunk 1
        if len(chunks) > 1:
            last_sentence = chunks[0].split(". ")[-1] if ". " in chunks[0] else chunks[0][-20:]
            assert any(last_sentence in chunk for chunk in chunks[1:]), \
                f"Overlap not found: last sentence {last_sentence!r} not in later chunks"
    
    def test_chunk_empty_text(self):
        """Test that empty text returns empty list."""
        chunks = chunk_text("", max_chunk_size=100)
        assert chunks == [""]


class TestChunkBySections:
    """Tests for structural chunk_by_sections (Phase 2)."""

    def test_chunk_by_sections_respects_section_boundaries(self):
        """Sections split on ## Combat and ## Movement should not be merged."""
        # Use text long enough to trigger splitting (exceeds max_chunk_size)
        intro = "Intro text. " * 30
        combat = "Combat rules here. Wrath dice. " * 30
        movement = "Movement rules. " * 20
        text = f"{intro}\n\n## Combat\n{combat}\n\n## Movement\n{movement}"
        chunks = chunk_by_sections(text, max_chunk_size=200, overlap=0)
        # Should have at least 2 chunks (Combat and Movement as separate sections)
        combat_chunks = [c for c in chunks if "## Combat" in c or "Combat rules" in c]
        movement_chunks = [c for c in chunks if "## Movement" in c or "Movement rules" in c]
        assert len(combat_chunks) >= 1, "Combat section should be in its own chunk"
        assert len(movement_chunks) >= 1, "Movement section should be in its own chunk"
        # No chunk should contain both section headers
        for c in chunks:
            assert not ("## Combat" in c and "## Movement" in c), "Sections should not be merged"

    def test_chunk_by_sections_falls_back_for_large_sections(self):
        """Section > max_chunk_size gets sentence-chunked via chunk_text."""
        # One large section with no internal section boundaries
        long_section = ". ".join([f"Sentence {i}." for i in range(200)])
        text = f"## BigSection\n{long_section}"
        chunks = chunk_by_sections(text, max_chunk_size=500, overlap=20)
        assert len(chunks) >= 2, "Large section should be split by sentence chunking"
        assert all(len(c) <= 500 + 50 for c in chunks), "Chunks should respect max size"

    def test_chunk_by_sections_short_text_unchanged(self):
        """Text under max_chunk_size returns single chunk."""
        text = "Short text with no sections."
        chunks = chunk_by_sections(text, max_chunk_size=1000)
        assert chunks == [text]


class TestCaching:
    """Tests for summary caching functionality."""
    
    def test_get_cached_summary_exists_txt(self, tmp_path):
        """Test retrieving cached summary from text file (legacy)."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        text_hash = "abc123"
        cache_file = cache_dir / f"{text_hash}.txt"
        cache_file.write_text("Cached summary text")
        
        result = get_cached_summary(text_hash, cache_dir)
        assert result is not None
        summary, metadata = result
        assert summary == "Cached summary text"
    
    def test_get_cached_summary_exists_json(self, tmp_path):
        """Test retrieving cached summary from JSON file (Phase 2)."""
        import json
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        text_hash = "abc123"
        cache_data = {
            "text_hash": text_hash,
            "summary": "Cached summary text",
            "metadata": {"provider": "openai", "cost": 0.01},
            "created_at": "2025-01-01T00:00:00"
        }
        cache_file = cache_dir / f"{text_hash}.json"
        cache_file.write_text(json.dumps(cache_data), encoding="utf-8")
        
        result = get_cached_summary(text_hash, cache_dir)
        assert result is not None
        summary, metadata = result
        assert summary == "Cached summary text"
        assert metadata["provider"] == "openai"
    
    def test_get_cached_summary_not_exists(self, tmp_path):
        """Test retrieving cached summary when it doesn't exist."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        text_hash = "nonexistent"
        
        result = get_cached_summary(text_hash, cache_dir)
        assert result is None
    
    def test_save_summary_cache(self, tmp_path):
        """Test saving summary to cache."""
        cache_dir = tmp_path / "cache"
        text_hash = "abc123"
        summary = "Test summary text"
        
        save_summary_cache(text_hash, summary, cache_dir)
        
        # Should create both txt and json files
        txt_file = cache_dir / f"{text_hash}.txt"
        json_file = cache_dir / f"{text_hash}.json"
        assert txt_file.exists()
        assert json_file.exists()
        assert txt_file.read_text() == summary
    
    def test_save_summary_cache_with_metadata(self, tmp_path):
        """Test saving summary to cache with metadata (Phase 2)."""
        import json
        cache_dir = tmp_path / "cache"
        text_hash = "abc123"
        summary = "Test summary"
        metadata = {"provider": "openai", "cost": 0.01, "tokens_used": 100}
        
        save_summary_cache(text_hash, summary, cache_dir, metadata)
        
        json_file = cache_dir / f"{text_hash}.json"
        assert json_file.exists()
        cache_data = json.loads(json_file.read_text())
        assert cache_data["summary"] == summary
        assert cache_data["metadata"] == metadata
    
    def test_save_summary_cache_creates_dir(self, tmp_path):
        """Test that cache directory is created if it doesn't exist."""
        cache_dir = tmp_path / "new_cache"
        text_hash = "abc123"
        summary = "Test summary"
        
        save_summary_cache(text_hash, summary, cache_dir)
        
        assert cache_dir.exists()
        assert (cache_dir / f"{text_hash}.txt").exists()


class TestSummarizeText:
    """Tests for text summarization."""
    
    def test_summarize_empty_text(self):
        """Test that empty text returns None."""
        result = summarize_text("")
        assert result is None
    
    def test_summarize_openai_not_available(self):
        """Test that OpenAI summarization fails gracefully when library unavailable."""
        with patch("ai_summarizer.OPENAI_AVAILABLE", False):
            result = summarize_text("Test text", provider="openai")
            assert result is None
    
    def test_summarize_anthropic_not_available(self):
        """Test that Anthropic summarization fails gracefully when library unavailable."""
        with patch("ai_summarizer.ANTHROPIC_AVAILABLE", False):
            result = summarize_text("Test text", provider="anthropic")
            assert result is None
    
    def test_summarize_ollama_not_available(self):
        """Test that Ollama summarization fails gracefully when library unavailable."""
        with patch("ai_summarizer.OLLAMA_AVAILABLE", False):
            result = summarize_text("Test text", provider="ollama")
            assert result is None
    
    @pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI library not available")
    def test_summarize_with_openai_mock(self):
        """Test OpenAI summarization with mocked API."""
        with patch("ai_summarizer.openai") as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Mocked summary"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.OpenAI.return_value = mock_client
            
            result = summarize_text("Test text", provider="openai", api_key="test-key")
            assert result == "Mocked summary"
    
    @pytest.mark.skipif(not ANTHROPIC_AVAILABLE, reason="Anthropic library not available")
    def test_summarize_with_anthropic_mock(self):
        """Test Anthropic summarization with mocked API."""
        with patch("ai_summarizer.anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.content = [MagicMock()]
            mock_response.content[0].text = "Mocked summary"
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.Anthropic.return_value = mock_client
            
            result = summarize_text("Test text", provider="anthropic", api_key="test-key")
            assert result == "Mocked summary"
    
    @pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="Ollama library not available")
    def test_summarize_with_ollama_mock(self):
        """Test Ollama summarization with mocked API."""
        with patch("ai_summarizer.ollama") as mock_ollama:
            mock_ollama.chat.return_value = {
                "message": {"content": "Mocked summary"},
                "prompt_eval_count": 10,
                "eval_count": 20
            }
            
            result = summarize_text("Test text", provider="ollama")
            assert result == "Mocked summary"
    
    @pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="Ollama library not available")
    def test_summarize_ollama_without_api_key(self):
        """Test that Ollama works without api_key parameter."""
        with patch("ai_summarizer.ollama") as mock_ollama:
            mock_ollama.chat.return_value = {
                "message": {"content": "Mocked summary"},
                "prompt_eval_count": 10,
                "eval_count": 20
            }
            
            # Should work without api_key
            result = summarize_text("Test text", provider="ollama", api_key=None)
            assert result == "Mocked summary"
    
    @pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="Ollama library not available")
    def test_summarize_ollama_with_endpoint(self):
        """Test Ollama summarization with custom endpoint."""
        with patch("ai_summarizer.ollama") as mock_ollama, \
             patch("os.environ") as mock_env:
            mock_ollama.chat.return_value = {
                "message": {"content": "Mocked summary"},
                "prompt_eval_count": 10,
                "eval_count": 20
            }
            
            result = summarize_text(
                "Test text", 
                provider="ollama",
                ollama_endpoint="http://custom-host:11434"
            )
            assert result == "Mocked summary"
    
    def test_summarize_default_provider_ollama(self):
        """Test that default provider is now ollama."""
        # Default should be ollama (not openai)
        # We can't easily test this without mocking, but we can verify the function signature
        import inspect
        sig = inspect.signature(summarize_text)
        assert sig.parameters["provider"].default == "ollama"
        assert sig.parameters["model"].default == "llama2"
    
    def test_summarize_unknown_provider(self):
        """Test that unknown provider returns None."""
        result = summarize_text("Test text", provider="unknown")
        assert result is None
    
    def test_summarize_chunks_long_text(self):
        """Test that long text is chunked before summarization."""
        long_text = ". ".join([f"Sentence {i}" for i in range(1000)])
        
        with patch("ai_summarizer.OPENAI_AVAILABLE", True), \
             patch("ai_summarizer._call_openai_api") as mock_call:
            mock_call.return_value = ("Summary", {"tokens_used": 10})
            result = summarize_text(long_text, provider="openai", api_key="test")
            assert mock_call.called


class TestIntegration:
    """Integration tests for AI summarizer."""
    
    def test_module_imports(self):
        """Test that AI summarizer module can be imported."""
        import ai_summarizer
        assert hasattr(ai_summarizer, "summarize_text")
        assert hasattr(ai_summarizer, "chunk_text")
        assert hasattr(ai_summarizer, "get_cached_summary")
        assert hasattr(ai_summarizer, "save_summary_cache")
    
    def test_provider_availability_flags(self):
        """Test that provider availability flags are set correctly."""
        from ai_summarizer import OPENAI_AVAILABLE, ANTHROPIC_AVAILABLE, OLLAMA_AVAILABLE
        assert isinstance(OPENAI_AVAILABLE, bool)
        assert isinstance(ANTHROPIC_AVAILABLE, bool)
        assert isinstance(OLLAMA_AVAILABLE, bool)


class TestAPICalls:
    """Tests for API call functions (Phase 2)."""
    
    @pytest.mark.unit
    @pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI library not available")
    def test_call_openai_api_success(self):
        """Test successful OpenAI API call."""
        with patch("ai_summarizer.openai") as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Test summary"
            mock_response.usage.total_tokens = 100
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.OpenAI.return_value = mock_client
            
            summary, metadata = _call_openai_api("Test prompt", "gpt-4", None, 500, 0.7)
            
            assert summary == "Test summary"
            assert metadata is not None
            assert metadata["provider"] == "openai"
            assert metadata["tokens_used"] == 100
    
    @pytest.mark.unit
    @pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI library not available")
    def test_call_openai_api_retry_on_rate_limit(self):
        """Test retry logic on rate limit (Phase 2)."""
        import time

        class FakeRateLimitError(Exception):
            pass

        with patch("ai_summarizer.openai") as mock_openai, \
             patch("time.sleep") as mock_sleep:
            mock_openai.RateLimitError = FakeRateLimitError
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Test summary"
            mock_response.usage.total_tokens = 100

            mock_client.chat.completions.create.side_effect = [
                FakeRateLimitError("Rate limit"),
                mock_response,
            ]
            mock_openai.OpenAI.return_value = mock_client

            summary, metadata = _call_openai_api("Test prompt", "gpt-4", None, 500, 0.7, max_retries=3)

            assert summary == "Test summary"
            assert mock_sleep.called  # Should have slept for retry
    
    @pytest.mark.unit
    @pytest.mark.skipif(not ANTHROPIC_AVAILABLE, reason="Anthropic library not available")
    def test_call_anthropic_api_success(self):
        """Test successful Anthropic API call."""
        with patch("ai_summarizer.anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.content = [MagicMock()]
            mock_response.content[0].text = "Test summary"
            mock_response.usage.input_tokens = 50
            mock_response.usage.output_tokens = 50
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.Anthropic.return_value = mock_client
            
            summary, metadata = _call_anthropic_api("Test prompt", "claude-3-sonnet", None, 500, 0.7)
            
            assert summary == "Test summary"
            assert metadata is not None
            assert metadata["provider"] == "anthropic"
            assert metadata["tokens_used"] == 100
    
    @pytest.mark.unit
    @pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="Ollama library not available")
    def test_call_ollama_api_success(self):
        """Test successful Ollama API call."""
        with patch("ai_summarizer.ollama") as mock_ollama:
            mock_ollama.chat.return_value = {
                "message": {"content": "Test summary"},
            }
            
            summary, metadata = _call_ollama_api("Test prompt", "llama2", 100, 0.7)
            
            assert summary == "Test summary"
            assert metadata is not None
            assert metadata["provider"] == "ollama"
            assert metadata["cost"] == 0.0


class TestCostTracking:
    """Tests for cost tracking (Phase 2)."""
    
    @pytest.mark.unit
    def test_calculate_openai_cost(self):
        """Test OpenAI cost calculation."""
        cost = _calculate_openai_cost("gpt-4", 1000)
        assert cost is not None
        assert cost > 0
    
    @pytest.mark.unit
    def test_calculate_anthropic_cost(self):
        """Test Anthropic cost calculation."""
        cost = _calculate_anthropic_cost("claude-3-sonnet", 1000)
        assert cost is not None
        assert cost > 0
    
    @pytest.mark.unit
    def test_calculate_cost_none_tokens(self):
        """Test cost calculation with None tokens."""
        cost = _calculate_openai_cost("gpt-4", None)
        assert cost is None


class TestPromptTemplates:
    """Tests for prompt templates (Phase 2)."""
    
    @pytest.mark.unit
    def test_get_rpg_prompt_template(self):
        """Test RPG prompt template generation."""
        template = _get_rpg_prompt_template()
        assert "{text}" in template
        assert "RPG" in template or "Wrath" in template or "Warhammer" in template
    
    @pytest.mark.unit
    def test_get_generic_prompt_template(self):
        """Test generic prompt template generation."""
        template = _get_generic_prompt_template()
        assert "{text}" in template
    
    @pytest.mark.unit
    def test_prompt_template_formatting(self):
        """Test that prompt templates can be formatted."""
        template = _get_rpg_prompt_template()
        formatted = template.format(text="Test document text")
        assert "Test document text" in formatted
        assert "{text}" not in formatted
