#!/usr/bin/env python3
"""
Quick verification script to check Ollama setup.
Run this to verify everything is configured correctly.
"""

from ai_summarizer import (
    check_ollama_health,
    check_model_available,
    summarize_text,
    OLLAMA_AVAILABLE,
)

def main():
    print("=" * 60)
    print("Ollama Setup Verification")
    print("=" * 60)
    print()
    
    # Check library availability
    print("1. Checking Ollama library...")
    if OLLAMA_AVAILABLE:
        print("   [OK] Ollama Python library is installed")
    else:
        print("   [FAIL] Ollama Python library not found")
        print("   Install with: pip install ollama")
        return
    print()
    
    # Check health
    print("2. Checking Ollama service...")
    if check_ollama_health():
        print("   [OK] Ollama service is running")
    else:
        print("   [FAIL] Ollama service is not accessible")
        print("   Make sure Ollama is installed and running")
        return
    print()
    
    # Check model
    print("3. Checking llama2 model...")
    if check_model_available("llama2"):
        print("   [OK] llama2 model is installed")
    else:
        print("   [FAIL] llama2 model not found")
        print("   Install with: ollama pull llama2")
        return
    print()
    
    # Test summarization
    print("4. Testing summarization...")
    test_text = """
    Warhammer 40,000: Wrath & Glory is a tabletop role-playing game set in the 
    grim darkness of the far future. Players take on the roles of various characters 
    in the Imperium of Man, fighting against chaos, xenos, and other threats. The game 
    uses a dice pool system and focuses on narrative storytelling.
    """
    
    try:
        summary = summarize_text(
            test_text.strip(),
            provider="ollama",
            model="llama2",
            max_tokens=100,
            temperature=0.7
        )
        
        if summary:
            print("   [OK] Summarization successful!")
            print(f"   Summary preview: {summary[:100]}...")
        else:
            print("   [FAIL] Summarization failed (returned None)")
            return
    except Exception as e:
        print(f"   [FAIL] Summarization error: {e}")
        return
    print()
    
    print("=" * 60)
    print("[OK] All checks passed! Ollama is ready to use.")
    print("=" * 60)
    print()
    print("Your PDF ingestion system will now use Ollama for AI summarization")
    print("by default. No API keys required!")

if __name__ == "__main__":
    main()
