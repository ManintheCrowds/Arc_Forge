# PURPOSE: Verify RAG Pipeline Outputs
# DEPENDENCIES: PowerShell 5.1+, JSON parsing
# MODIFICATION NOTES: Validates file existence, JSON structure, entity quality, and hallucination detection

param(
    [string]$OutputDir = "D:\arc_forge\ObsidianVault\Campaigns\_rag_outputs",
    [string]$CampaignKBRoot = "D:\arc_forge\campaign_kb"
)

$ErrorActionPreference = "Continue"
$report = @{
    "timestamp" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "checks" = @{}
    "warnings" = @()
    "errors" = @()
    "summary" = @{}
}

Write-Host "=== RAG Pipeline Output Verification ===" -ForegroundColor Cyan
Write-Host "Output Directory: $OutputDir" -ForegroundColor Gray
Write-Host "Campaign KB Root: $CampaignKBRoot`n" -ForegroundColor Gray

# 1. Check File Existence
Write-Host "[1/5] Checking file existence..." -ForegroundColor Yellow
$requiredFiles = @(
    "rag_patterns.json",
    "rag_patterns.md",
    "rag_context_summary.md",
    "rag_generated_rules.md",
    "rag_generated_adventure.md",
    "rag_generated_bios.md"
)

$filesExist = $true
$existingFiles = @()
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $OutputDir $file
    if (Test-Path $filePath) {
        $existingFiles += $file
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        $filesExist = $false
        $report.errors += "Missing file: $file"
        Write-Host "  ✗ $file (MISSING)" -ForegroundColor Red
    }
}

$report.checks["file_existence"] = @{
    "passed" = $filesExist
    "found" = $existingFiles.Count
    "expected" = $requiredFiles.Count
}

# 2. Validate JSON Structure
Write-Host "`n[2/5] Validating JSON structure..." -ForegroundColor Yellow
$jsonValid = $false
$patternsData = $null

$patternsPath = Join-Path $OutputDir "rag_patterns.json"
if (Test-Path $patternsPath) {
    try {
        $jsonContent = Get-Content $patternsPath -Raw -Encoding UTF8
        $patternsData = $jsonContent | ConvertFrom-Json
        $jsonValid = $true
        
        # Check required top-level keys
        $requiredKeys = @("entities", "entity_counts", "themes", "source_docs")
        $missingKeys = @()
        foreach ($key in $requiredKeys) {
            if (-not $patternsData.PSObject.Properties.Name -contains $key) {
                $missingKeys += $key
            }
        }
        
        if ($missingKeys.Count -eq 0) {
            Write-Host "  ✓ JSON structure valid" -ForegroundColor Green
            $report.checks["json_structure"] = @{
                "passed" = $true
                "has_entities" = ($null -ne $patternsData.entities)
                "has_themes" = ($null -ne $patternsData.themes)
                "has_source_docs" = ($null -ne $patternsData.source_docs)
            }
        } else {
            $report.errors += "JSON missing required keys: $($missingKeys -join ', ')"
            Write-Host "  ✗ JSON missing keys: $($missingKeys -join ', ')" -ForegroundColor Red
        }
    } catch {
        $jsonValid = $false
        $report.errors += "JSON parse error: $($_.Exception.Message)"
        Write-Host "  ✗ JSON parse error: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    $report.errors += "Cannot validate JSON: rag_patterns.json not found"
}

# 3. Entity Quality Check
Write-Host "`n[3/5] Checking entity quality..." -ForegroundColor Yellow
$suspiciousEntities = @()

if ($null -ne $patternsData -and $null -ne $patternsData.entities) {
    $entityTypes = @("NPCs", "Factions", "Locations", "Items")
    
    foreach ($type in $entityTypes) {
        if ($null -ne $patternsData.entities.$type) {
            foreach ($entity in $patternsData.entities.$type) {
                # Flag suspicious patterns
                $isSuspicious = $false
                $reason = ""
                
                # Too long (likely a sentence fragment)
                if ($entity.Length -gt 50) {
                    $isSuspicious = $true
                    $reason = "Too long ($($entity.Length) chars)"
                }
                # Contains common words that suggest it's not a proper name
                elseif ($entity -match "^(the|a|an|in|on|at|to|for|of|and|or|but|during|motion|avoid|board|carrying|tied|reveals|triggering|escalation|system|world|station|approach|across|via|optional|preserve|extracting|stabilize|rich|spiritually|cursed|home|base|command|center|intel|leverage|over|old|hulk|memory|echoes|may|map|hidden|warp|nodes|psyk|vector|older|heist|infiltration|geothermal|glacial|hive|plains|ice)$") {
                    $isSuspicious = $true
                    $reason = "Contains common words (likely sentence fragment)"
                }
                # All lowercase or all uppercase (unusual for proper names)
                elseif (($entity -cmatch "^[a-z\s]+$" -and $entity.Length -gt 3) -or ($entity -cmatch "^[A-Z\s]+$" -and $entity.Length -gt 3)) {
                    $isSuspicious = $true
                    $reason = "Unusual capitalization"
                }
                
                if ($isSuspicious) {
                    $suspiciousEntities += @{
                        "type" = $type
                        "entity" = $entity
                        "reason" = $reason
                    }
                    Write-Host "  ⚠ Suspicious $type`: $entity ($reason)" -ForegroundColor Yellow
                }
            }
        }
    }
    
    $report.checks["entity_quality"] = @{
        "passed" = ($suspiciousEntities.Count -eq 0)
        "suspicious_count" = $suspiciousEntities.Count
        "suspicious_entities" = $suspiciousEntities
    }
    
    if ($suspiciousEntities.Count -eq 0) {
        Write-Host "  ✓ No suspicious entities found" -ForegroundColor Green
    } else {
        $report.warnings += "Found $($suspiciousEntities.Count) suspicious entities"
    }
} else {
    $report.warnings += "Cannot check entity quality: patterns data not loaded"
}

# 4. Hallucination Detection
Write-Host "`n[4/5] Checking for hallucinations in generated content..." -ForegroundColor Yellow

# Load source documents for comparison
$sourceText = ""
$sourceDocs = @()
if (Test-Path $CampaignKBRoot) {
    $campaignDir = Join-Path $CampaignKBRoot "campaign"
    if (Test-Path $campaignDir) {
        $mdFiles = Get-ChildItem -Path $campaignDir -Filter "*.md" -Recurse
        foreach ($file in $mdFiles) {
            try {
                $content = Get-Content $file.FullName -Raw -Encoding UTF8
                $sourceText += " $content"
                $sourceDocs += $file.Name
            } catch {
                Write-Host "  ⚠ Could not read source: $($file.Name)" -ForegroundColor Yellow
            }
        }
    }
}

$sourceTextLower = $sourceText.ToLower()
$hallucinations = @()

# Check generated rules
$rulesPath = Join-Path $OutputDir "rag_generated_rules.md"
if (Test-Path $rulesPath) {
    $rulesContent = Get-Content $rulesPath -Raw -Encoding UTF8
    
    # Extract potential item/artifact mentions (common hallucination patterns)
    $itemPatterns = @(
        "(?i)(daemon\s+slayer|warpstone\s+amulet|ancient\s+artifact|powerful\s+weapon|magical\s+item|relic|artifact|legendary\s+.*?)"
    )
    
    foreach ($pattern in $itemPatterns) {
        $matches = [regex]::Matches($rulesContent, $pattern)
        foreach ($match in $matches) {
            $mentioned = $match.Value
            # Check if this exact phrase appears in source documents
            if ($sourceTextLower -notmatch [regex]::Escape($mentioned.ToLower())) {
                # Check if individual words appear (might be legitimate combination)
                $words = $mentioned -split "\s+"
                $wordCount = ($words | Where-Object { $sourceTextLower -match [regex]::Escape($_.ToLower()) }).Count
                if ($wordCount -lt ($words.Count * 0.5)) {
                    $hallucinations += @{
                        "file" = "rag_generated_rules.md"
                        "mention" = $mentioned
                        "type" = "potential_hallucination"
                    }
                    Write-Host "  ⚠ Potential hallucination in rules: '$mentioned'" -ForegroundColor Yellow
                }
            }
        }
    }
}

# Check generated adventure
$adventurePath = Join-Path $OutputDir "rag_generated_adventure.md"
if (Test-Path $adventurePath) {
    $adventureContent = Get-Content $adventurePath -Raw -Encoding UTF8
    
    # Check for non-canonical item mentions
    if ($adventureContent -match "(?i)(daemon\s+slayer|warpstone\s+amulet)") {
        $hallucinations += @{
            "file" = "rag_generated_adventure.md"
            "mention" = $matches[0]
            "type" = "potential_hallucination"
        }
        Write-Host "  ⚠ Potential hallucination in adventure: '$($matches[0])'" -ForegroundColor Yellow
    }
}

$report.checks["hallucination_detection"] = @{
    "passed" = ($hallucinations.Count -eq 0)
    "found" = $hallucinations.Count
    "hallucinations" = $hallucinations
    "source_docs_checked" = $sourceDocs.Count
}

if ($hallucinations.Count -eq 0) {
    Write-Host "  ✓ No obvious hallucinations detected" -ForegroundColor Green
} else {
    $report.warnings += "Found $($hallucinations.Count) potential hallucinations"
}

# 5. Theme Validation
Write-Host "`n[5/5] Validating theme counts..." -ForegroundColor Yellow
if ($null -ne $patternsData -and $null -ne $patternsData.themes) {
    $themeIssues = @()
    
    foreach ($theme in $patternsData.themes.PSObject.Properties) {
        $count = $theme.Value
        $themeName = $theme.Name
        
        # Flag if count seems unreasonable (too high might indicate over-counting)
        if ($count -gt 100) {
            $themeIssues += @{
                "theme" = $themeName
                "count" = $count
                "issue" = "Very high count (possible over-counting)"
            }
            Write-Host "  ⚠ Theme '$themeName': count $count (very high)" -ForegroundColor Yellow
        } elseif ($count -eq 0) {
            $themeIssues += @{
                "theme" = $themeName
                "count" = $count
                "issue" = "Zero count (theme may not be present)"
            }
        }
    }
    
    $report.checks["theme_validation"] = @{
        "passed" = ($themeIssues.Count -eq 0)
        "theme_count" = $patternsData.themes.PSObject.Properties.Count
        "issues" = $themeIssues
    }
    
    if ($themeIssues.Count -eq 0) {
        Write-Host "  ✓ Theme counts appear reasonable" -ForegroundColor Green
    }
} else {
    $report.warnings += "Cannot validate themes: patterns data not loaded"
}

# Generate Summary
Write-Host "`n=== Verification Summary ===" -ForegroundColor Cyan
$totalChecks = $report.checks.Count
$passedChecks = ($report.checks.Values | Where-Object { $_.passed }).Count
$failedChecks = $totalChecks - $passedChecks

$report.summary = @{
    "total_checks" = $totalChecks
    "passed" = $passedChecks
    "failed" = $failedChecks
    "warnings" = $report.warnings.Count
    "errors" = $report.errors.Count
}

Write-Host "Checks: $passedChecks/$totalChecks passed" -ForegroundColor $(if ($failedChecks -eq 0) { "Green" } else { "Yellow" })
Write-Host "Warnings: $($report.warnings.Count)" -ForegroundColor $(if ($report.warnings.Count -eq 0) { "Green" } else { "Yellow" })
Write-Host "Errors: $($report.errors.Count)" -ForegroundColor $(if ($report.errors.Count -eq 0) { "Green" } else { "Red" })

# Save report
$reportPath = Join-Path $OutputDir "verification_report.json"
try {
    $report | ConvertTo-Json -Depth 10 | Set-Content $reportPath -Encoding UTF8
    Write-Host "`nReport saved to: $reportPath" -ForegroundColor Gray
} catch {
    Write-Host "`nWarning: Could not save report: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Exit with appropriate code
if ($report.errors.Count -gt 0) {
    exit 1
} elseif ($failedChecks -gt 0 -or $report.warnings.Count -gt 0) {
    exit 2
} else {
    exit 0
}
