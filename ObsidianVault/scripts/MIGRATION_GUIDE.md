# Migration Guide: API-Based to Self-Hosted LLM (Ollama)

## Overview

This guide helps you migrate from API-based LLM providers (OpenAI, Anthropic) to self-hosted Ollama for AI summarization and entity extraction in the PDF ingestion system.

## Benefits of Migration

- **No API Keys Required**: Eliminates dependency on external API services
- **Cost Savings**: No per-token charges (only hardware costs)
- **Privacy**: All processing happens locally
- **No Rate Limits**: Process as many documents as your hardware allows
- **Offline Capability**: Works without internet connection

## Prerequisites

1. **Hardware Requirements**:
   - CPU: Modern multi-core processor recommended
   - RAM: At least 8GB (16GB+ recommended for larger models)
   - GPU: Optional but recommended for faster inference (NVIDIA GPU with CUDA support)
   - Storage: 5-20GB free space for models

2. **Software Requirements**:
   - Windows 10/11 (or Linux/macOS)
   - Python 3.8+
   - Ollama installed and running

## Step 1: Install Ollama

### Windows

1. Download Ollama installer from: https://ollama.ai/download
2. Run the installer and follow the setup wizard
3. Verify installation:
   ```powershell
   ollama --version
   ```

### Linux/macOS

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## Step 2: Download a Model

Ollama requires you to download models before use. Recommended models:

- **llama2** (7B parameters, ~4GB): Good balance of quality and speed
- **mistral** (7B parameters, ~4GB): Fast and efficient
- **llama2:13b** (13B parameters, ~7GB): Higher quality, slower

Download a model:
```bash
ollama pull llama2
```

Verify installation:
```bash
ollama list
```

Test the model:
```bash
ollama run llama2 "Hello, how are you?"
```

## Step 3: Install Python Dependencies

```bash
pip install ollama
```

## Step 4: Update Configuration

### Option A: Quick Migration (Use Defaults)

Update `ingest_config.json`:

```json
{
  "ai_summarization": {
    "enabled": true,
    "provider": "ollama",
    "model": "llama2",
    "api_key": null,
    "max_tokens": 500,
    "temperature": 0.7,
    "cache_enabled": true,
    "cache_dir": "Sources/_summaries",
    "ollama_endpoint": null
  },
  "entity_extraction": {
    "use_llm": false,
    "llm_provider": "ollama",
    "llm_model": "llama2",
    "llm_api_key": null
  }
}
```

### Option B: Custom Endpoint

If Ollama is running on a different machine or port:

```json
{
  "ai_summarization": {
    "provider": "ollama",
    "model": "llama2",
    "ollama_endpoint": "http://192.168.1.100:11434"
  }
}
```

Or set environment variable:
```powershell
$env:OLLAMA_HOST = "http://192.168.1.100:11434"
```

## Step 5: Verify Setup

### Health Check

The system includes health check functions. You can verify Ollama is accessible:

```python
from ai_summarizer import check_ollama_health, check_model_available

# Check if Ollama is running
if check_ollama_health():
    print("Ollama is running!")
else:
    print("Ollama is not accessible. Please start Ollama service.")

# Check if your model is available
if check_model_available("llama2"):
    print("Model 'llama2' is available!")
else:
    print("Model not found. Run: ollama pull llama2")
```

### Test Summarization

Run a test ingestion to verify everything works:

```bash
python ingest_pdfs.py --pdf-root "path/to/test/pdf"
```

Check the generated source note for an "AI Summary" section.

## Step 6: Performance Tuning

### Model Selection

- **Small models (7B)**: Faster, lower quality, less RAM
- **Large models (13B+)**: Slower, higher quality, more RAM

### Temperature Settings

- Lower (0.3-0.5): More focused, deterministic summaries
- Higher (0.7-0.9): More creative, varied summaries

### Max Tokens

- 300-500: Short summaries
- 500-1000: Medium summaries
- 1000+: Long summaries (slower)

## Troubleshooting

### Issue: "Ollama library not available"

**Solution**: Install the Python library:
```bash
pip install ollama
```

### Issue: "Ollama connection error"

**Solution**: 
1. Verify Ollama is running: `ollama list`
2. Check endpoint configuration matches Ollama's actual endpoint
3. On Windows, ensure Ollama service is started

### Issue: "Model 'llama2' not found"

**Solution**: Download the model:
```bash
ollama pull llama2
```

### Issue: Slow performance

**Solutions**:
1. Use a smaller model (7B instead of 13B)
2. Reduce `max_tokens` setting
3. Enable GPU acceleration (if available)
4. Close other applications to free up RAM

### Issue: Out of memory errors

**Solutions**:
1. Use a smaller model
2. Reduce `max_tokens`
3. Add more RAM
4. Use CPU offloading (if supported by your setup)

## Rollback to API Providers

If you need to switch back to API providers:

1. Update config:
```json
{
  "ai_summarization": {
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "sk-your-key-here"
  }
}
```

2. The system will automatically use the API provider instead of Ollama.

## Before/After Comparison

### Before (API-Based)

```json
{
  "ai_summarization": {
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "sk-...",
    "max_tokens": 500
  }
}
```

**Characteristics**:
- Requires internet connection
- API key needed
- Per-token costs
- Rate limits apply
- Data sent to external service

### After (Self-Hosted)

```json
{
  "ai_summarization": {
    "provider": "ollama",
    "model": "llama2",
    "api_key": null,
    "ollama_endpoint": null,
    "max_tokens": 500
  }
}
```

**Characteristics**:
- Works offline
- No API key needed
- No per-token costs
- No rate limits
- All processing local

## Common Issues and Solutions

### Issue: Summaries are shorter/different quality

**Explanation**: Local models may produce different quality summaries than cloud APIs. This is expected.

**Solutions**:
- Try a larger model (13B instead of 7B)
- Adjust temperature settings
- Increase max_tokens
- Use a different model (mistral, codellama, etc.)

### Issue: First request is very slow

**Explanation**: Models are loaded into memory on first use.

**Solution**: This is normal. Subsequent requests will be faster.

### Issue: Multiple models consuming disk space

**Solution**: Remove unused models:
```bash
ollama rm model-name
```

List all models:
```bash
ollama list
```

## Next Steps

1. **Monitor Performance**: Check logs for any errors or warnings
2. **Adjust Settings**: Tune temperature, max_tokens based on your needs
3. **Experiment with Models**: Try different models to find the best fit
4. **Enable Entity Extraction**: Set `entity_extraction.use_llm = true` if desired

## Support

For issues or questions:
- Check Ollama documentation: https://ollama.ai/docs
- Review system logs: `scripts/ingest_diagnostic.log` (if enabled)
- Verify Ollama health: Use `check_ollama_health()` function

## Migration Checklist

- [ ] Ollama installed and verified
- [ ] At least one model downloaded
- [ ] Python `ollama` library installed
- [ ] Configuration updated with `provider: "ollama"`
- [ ] Health check passes
- [ ] Test ingestion successful
- [ ] AI summaries generated correctly
- [ ] Performance acceptable
- [ ] Old API keys removed (optional, for security)

---

**Note**: This migration maintains backward compatibility. You can switch between providers by changing the `provider` field in the config. API keys are only required for `openai` and `anthropic` providers, not for `ollama`.
