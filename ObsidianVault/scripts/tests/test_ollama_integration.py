# PURPOSE: Integration tests for Ollama functionality.
# DEPENDENCIES: pytest, ai_summarizer module, optional Ollama installation.
# MODIFICATION NOTES: Tests end-to-end Ollama integration.

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from ai_summarizer import (
    summarize_text,
    check_ollama_health,
    check_model_available,
    OLLAMA_AVAILABLE,
)


class TestOllamaIntegration:
    """Integration tests for Ollama summarization."""
    
    @pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="Ollama library not available")
    def test_end_to_end_summarization_mock(self):
        """Test end-to-end summarization flow with Ollama (mocked)."""
        with patch("ai_summarizer.ollama") as mock_ollama:
            # Mock successful response
            mock_ollama.chat.return_value = {
                "message": {"content": "This is a test summary of the document."},
                "prompt_eval_count": 50,
                "eval_count": 30
            }
            
            text = "This is a long document that needs to be summarized. " * 10
            result = summarize_text(
                text,
                provider="ollama",
                model="llama2",
                api_key=None,  # Should work without API key
                max_tokens=100,
                temperature=0.7
            )
            
            assert result is not None
            assert "summary" in result.lower() or len(result) > 0
            mock_ollama.chat.assert_called()
    
    @pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="Ollama library not available")
    def test_summarization_with_caching(self, tmp_path):
        """Test that Ollama summaries are cached correctly."""
        cache_dir = tmp_path / "cache"
        
        with patch("ai_summarizer.ollama") as mock_ollama:
            mock_ollama.chat.return_value = {
                "message": {"content": "Cached summary"},
                "prompt_eval_count": 20,
                "eval_count": 15
            }
            
            text = "Test document text"
            
            # First call - should generate summary
            result1 = summarize_text(
                text,
                provider="ollama",
                model="llama2",
                cache_dir=cache_dir
            )
            
            assert result1 is not None
            assert mock_ollama.chat.call_count == 1
            
            # Second call - should use cache
            with patch("ai_summarizer.ollama") as mock_ollama2:
                result2 = summarize_text(
                    text,
                    provider="ollama",
                    model="llama2",
                    cache_dir=cache_dir
                )
                
                # Should be same result
                assert result2 == result1
                # Should not call Ollama again (cached)
                assert mock_ollama2.chat.call_count == 0
    
    @pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="Ollama library not available")
    def test_summarization_with_chunking(self):
        """Test that long documents are chunked correctly for Ollama."""
        # Create a very long text
        long_text = ". ".join([f"Sentence {i} with some content." for i in range(500)])
        
        with patch("ai_summarizer.ollama") as mock_ollama:
            mock_ollama.chat.return_value = {
                "message": {"content": "Chunk summary"},
                "prompt_eval_count": 100,
                "eval_count": 50
            }
            
            result = summarize_text(
                long_text,
                provider="ollama",
                model="llama2",
                max_tokens=500
            )
            
            # Should have called Ollama (possibly multiple times for chunks)
            assert mock_ollama.chat.called
    
    def test_health_check_integration(self):
        """Test health check integration (mocked)."""
        if not OLLAMA_AVAILABLE:
            # Test that it returns False when library not available
            result = check_ollama_health()
            assert result is False
        else:
            # Test with mock
            with patch("ai_summarizer.ollama") as mock_ollama:
                mock_ollama.list.return_value = {"models": []}
                
                result = check_ollama_health()
                assert isinstance(result, bool)
    
    def test_model_availability_integration(self):
        """Test model availability check integration (mocked)."""
        if not OLLAMA_AVAILABLE:
            # Test that it returns False when library not available
            result = check_model_available("llama2")
            assert result is False
        else:
            # Test with mock
            with patch("ai_summarizer.ollama") as mock_ollama:
                mock_ollama.list.return_value = {
                    "models": [
                        {"name": "llama2:latest"},
                        {"name": "mistral:latest"}
                    ]
                }
                
                result = check_model_available("llama2")
                assert result is True
                
                result = check_model_available("nonexistent")
                assert result is False
    
    @pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="Ollama library not available")
    def test_ollama_without_api_key(self):
        """Test that Ollama works without any API key configuration."""
        with patch("ai_summarizer.ollama") as mock_ollama:
            mock_ollama.chat.return_value = {
                "message": {"content": "Summary without API key"},
                "prompt_eval_count": 10,
                "eval_count": 5
            }
            
            # Should work with None api_key
            result = summarize_text(
                "Test text",
                provider="ollama",
                model="llama2",
                api_key=None
            )
            
            assert result is not None
            mock_ollama.chat.assert_called_once()
    
    @pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="Ollama library not available")
    def test_ollama_default_provider(self):
        """Test that Ollama is the default provider."""
        with patch("ai_summarizer.ollama") as mock_ollama:
            mock_ollama.chat.return_value = {
                "message": {"content": "Default provider summary"},
                "prompt_eval_count": 10,
                "eval_count": 5
            }
            
            # Call without specifying provider - should use Ollama default
            result = summarize_text("Test text")
            
            # Should have called Ollama (default provider)
            assert mock_ollama.chat.called
            assert result is not None
