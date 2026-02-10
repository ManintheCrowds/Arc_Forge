# PURPOSE: Comprehensive end-to-end RAG pipeline workflow test
# DEPENDENCIES: Python, rag_pipeline.py, ingest_config.json
# MODIFICATION NOTES: Tests incremental PDF ingestion, entity extraction, and content generation

param(
    [string]$Query = "combat modifiers",
    [string]$ConfigPath = "ingest_config.json"
)

Write-Host "=== RAG Pipeline End-to-End Workflow Test ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Configuration validation
Write-Host "[TEST 1] Validating configuration..." -ForegroundColor Yellow
$configCheck = python -c "
import json
from pathlib import Path
try:
    with open('$ConfigPath', 'r') as f:
        config = json.load(f)
    rag_config = config.get('rag_pipeline', {})
    print('Config loaded: RAG enabled=' + str(rag_config.get('enabled', False)))
    print('PDF ingestion: enabled=' + str(rag_config.get('include_pdfs', False)))
    pdf_ing = rag_config.get('pdf_ingestion', {})
    print('Chunk size: ' + str(pdf_ing.get('max_chunk_size', 'default')))
    print('Max chunks/PDF: ' + str(pdf_ing.get('max_chunks_per_pdf', 'default')))
    print('Max total chars: ' + str(pdf_ing.get('max_total_text_chars', 'default')))
except Exception as e:
    print(f'✗ Config error: {e}')
    exit(1)
"
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Configuration validation failed" -ForegroundColor Red
    exit 1
}
Write-Host $configCheck
Write-Host ""

# Test 2: PDF ingestion test
Write-Host "[TEST 2] Testing incremental PDF ingestion..." -ForegroundColor Yellow
$pdfTest = python -c "
import sys
sys.path.insert(0, '.')
from pathlib import Path
from rag_pipeline import read_pdf_texts, load_pipeline_config
import json

try:
    config = load_pipeline_config(Path('$ConfigPath'))
    rag_config = config.get('rag_pipeline', {})
    pdf_dir = Path(rag_config.get('pdf_extraction_dir', 'Sources/_extracted_text'))
    pdf_config = rag_config.get('pdf_ingestion', {})
    
    pdf_map = read_pdf_texts(
        pdf_dir,
        file_pattern=rag_config.get('pdf_file_pattern', '*.txt'),
        max_chunk_size=pdf_config.get('max_chunk_size', 50000),
        max_chunks_per_pdf=pdf_config.get('max_chunks_per_pdf', 10),
        max_total_text_chars=pdf_config.get('max_total_text_chars', 2000000),
    )
    
    total_chars = sum(len(v) for v in pdf_map.values())
    chunked_sources = [k for k in pdf_map.keys() if '[chunk' in k]
    unchunked_sources = [k for k in pdf_map.keys() if '[chunk' not in k]
    
    print('PDF sources loaded: ' + str(len(pdf_map)))
    print('Total characters: ' + str(total_chars))
    print('Chunked sources: ' + str(len(chunked_sources)))
    print('Unchunked sources: ' + str(len(unchunked_sources)))
    if chunked_sources:
        print('Sample chunked: ' + chunked_sources[0])
except Exception as e:
    print(f'✗ PDF ingestion error: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ PDF ingestion test failed" -ForegroundColor Red
    exit 1
}
Write-Host $pdfTest
Write-Host ""

# Test 3: Full pipeline run
Write-Host "[TEST 3] Running full RAG pipeline..." -ForegroundColor Yellow
Write-Host "Query: '$Query'" -ForegroundColor Gray
Write-Host ""

$pipelineOutput = python rag_pipeline.py --config $ConfigPath --query $Query 2>&1
$pipelineExitCode = $LASTEXITCODE

if ($pipelineExitCode -eq 0) {
    Write-Host "✓ Pipeline completed successfully" -ForegroundColor Green
    
    # Parse JSON output
    $jsonMatch = $pipelineOutput | Select-String -Pattern '\{.*"status".*"success".*\}'
    if ($jsonMatch) {
        try {
            $result = $jsonMatch.Matches[0].Value | ConvertFrom-Json
            Write-Host ""
            Write-Host "=== Pipeline Results ===" -ForegroundColor Cyan
            Write-Host "Status: $($result.status)" -ForegroundColor Green
            Write-Host ""
            Write-Host "Outputs:" -ForegroundColor Yellow
            $result.outputs.PSObject.Properties | ForEach-Object {
                Write-Host "  - $($_.Name): $($_.Value)" -ForegroundColor Gray
            }
            Write-Host ""
            
            if ($result.pattern_report) {
                Write-Host "Pattern Report:" -ForegroundColor Yellow
                $entities = $result.pattern_report.entities
                Write-Host "  - NPCs: $($entities.NPCs.Count)" -ForegroundColor Gray
                Write-Host "  - Factions: $($entities.Factions.Count)" -ForegroundColor Gray
                Write-Host "  - Locations: $($entities.Locations.Count)" -ForegroundColor Gray
                Write-Host "  - Items: $($entities.Items.Count)" -ForegroundColor Gray
                Write-Host ""
                
                $sourceDocs = $result.pattern_report.source_docs
                $pdfSources = $sourceDocs | Where-Object { $_ -like '*[PDF]*' }
                $campaignSources = $sourceDocs | Where-Object { $_ -notlike '*[PDF]*' }
                Write-Host "  - Total sources: $($sourceDocs.Count)" -ForegroundColor Gray
                Write-Host "  - PDF sources: $($pdfSources.Count)" -ForegroundColor Gray
                Write-Host "  - Campaign sources: $($campaignSources.Count)" -ForegroundColor Gray
                if ($pdfSources.Count -gt 0) {
                    Write-Host "  ✓ PDFs successfully ingested!" -ForegroundColor Green
                } else {
                    Write-Host "  ⚠ No PDF sources found in output" -ForegroundColor Yellow
                }
            }
            
            if ($result.query_context) {
                Write-Host "Query Context:" -ForegroundColor Yellow
                Write-Host "  - Retrieved contexts: $($result.query_context.Count)" -ForegroundColor Gray
                if ($result.query_context.Count -gt 0) {
                    $pdfContexts = $result.query_context | Where-Object { $_.source -like '*[PDF]*' }
                    Write-Host "  - PDF contexts: $($pdfContexts.Count)" -ForegroundColor Gray
                    if ($pdfContexts.Count -gt 0) {
                        Write-Host "  ✓ PDF content retrieved for query!" -ForegroundColor Green
                    }
                }
            }
        } catch {
            Write-Host "⚠ Could not parse JSON output: $_" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "✗ Pipeline failed with exit code $pipelineExitCode" -ForegroundColor Red
    Write-Host $pipelineOutput
    exit 1
}

Write-Host ""
Write-Host "=== Test Summary ===" -ForegroundColor Cyan
Write-Host "✓ Configuration validated" -ForegroundColor Green
Write-Host "✓ PDF ingestion tested" -ForegroundColor Green
Write-Host "✓ Full pipeline executed" -ForegroundColor Green
Write-Host ""
Write-Host "End-to-end workflow test complete!" -ForegroundColor Green
