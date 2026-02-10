<# 
# PURPOSE: Watch for new/updated PDFs and run ingestion.
# DEPENDENCIES: Python runtime, ingest_pdfs.py, ingest_config.json.
# MODIFICATION NOTES: Scheduled Task entrypoint with diagnostic mode.
#>

[CmdletBinding()]
param(
    [switch]$Diagnostic,
    [string]$LogPath = "",
    [switch]$EnableProfiling
)

$ErrorActionPreference = "Stop"

# PURPOSE: Write structured diagnostic log entry.
# DEPENDENCIES: Diagnostic mode enabled, log path configured.
# MODIFICATION NOTES: Writes JSON log entries for troubleshooting.
function Write-DiagnosticLog {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,
        [Parameter(Mandatory = $false)]
        [hashtable]$Data = @{},
        [Parameter(Mandatory = $false)]
        [string]$Level = "INFO"
    )

    if (-not $Diagnostic) { return }

    $logEntry = @{
        timestamp = (Get-Date -Format "o")
        level = $Level
        message = $Message
        data = $Data
    }

    $logLine = ($logEntry | ConvertTo-Json -Compress)
    
    if ($script:DiagnosticLogPath) {
        Add-Content -LiteralPath $script:DiagnosticLogPath -Value $logLine
    }
}

# PURPOSE: Cache PDF discovery results to avoid full scan every run.
# DEPENDENCIES: Cache file path, PDF root directory.
# MODIFICATION NOTES: Returns cached PDF list with modification times or $null. TTL increased to 30 minutes.
function Get-CachedPdfList {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CachePath,
        [Parameter(Mandatory = $true)]
        [string]$PdfRoot,
        [Parameter(Mandatory = $false)]
        [int]$CacheTTLMinutes = 30
    )

    if (-not (Test-Path -LiteralPath $CachePath)) {
        return $null
    }

    try {
        $cache = Get-Content -LiteralPath $CachePath -Raw | ConvertFrom-Json
        $cacheTime = [DateTime]::Parse($cache.cache_time).ToUniversalTime()
        $cacheAge = ((Get-Date).ToUniversalTime() - $cacheTime).TotalMinutes
        
        # Use cache if less than TTL minutes old (default 30 minutes)
        if ($cacheAge -lt $CacheTTLMinutes) {
            Write-DiagnosticLog -Message "Using cached PDF list" -Data @{ 
                cache_age_minutes = [math]::Round($cacheAge, 2)
                pdf_count = $cache.pdfs.Count
                cache_ttl_minutes = $CacheTTLMinutes
            }
            return $cache.pdfs
        } else {
            Write-DiagnosticLog -Message "Cache expired, will rescan" -Data @{ 
                cache_age_minutes = [math]::Round($cacheAge, 2)
                cache_ttl_minutes = $CacheTTLMinutes
            }
        }
    } catch {
        Write-DiagnosticLog -Message "Cache read failed, will rescan" -Data @{ 
            error = $_.Exception.Message
        } -Level "WARN"
    }

    return $null
}

# PURPOSE: Save PDF discovery results to cache.
# DEPENDENCIES: Cache file path, PDF list.
# MODIFICATION NOTES: Writes JSON cache with PDF paths and modification times.
function Save-CachedPdfList {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CachePath,
        [Parameter(Mandatory = $true)]
        [array]$PdfList
    )

    $cache = @{
        cache_time = (Get-Date).ToUniversalTime().ToString("o")
        pdfs = $PdfList
    }

    try {
        $cache | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $CachePath
        Write-DiagnosticLog -Message "PDF list cached" -Data @{ 
            cache_path = $CachePath
            pdf_count = $PdfList.Count
        }
    } catch {
        Write-DiagnosticLog -Message "Cache write failed" -Data @{ 
            error = $_.Exception.Message
        } -Level "WARN"
    }
}

# PURPOSE: Detect changes in PDF directory using incremental comparison.
# DEPENDENCIES: Cached PDF list, current PDF list.
# MODIFICATION NOTES: Returns hashtable with new, modified, and deleted PDFs.
function Get-PdfChanges {
    param(
        [Parameter(Mandatory = $true)]
        [array]$CachedPdfs,
        [Parameter(Mandatory = $true)]
        [array]$CurrentPdfs
    )

    $changes = @{
        New = @()
        Modified = @()
        Deleted = @()
    }

    # Create hashtable for quick lookup
    $cachedMap = @{}
    foreach ($pdf in $CachedPdfs) {
        $cachedMap[$pdf.Path] = $pdf
    }

    $currentMap = @{}
    foreach ($pdf in $CurrentPdfs) {
        $currentMap[$pdf.Path] = $pdf
    }

    # Find new and modified PDFs
    foreach ($pdf in $CurrentPdfs) {
        $path = $pdf.Path
        if (-not $cachedMap.ContainsKey($path)) {
            $changes.New += $pdf
        } else {
            $cachedTime = [DateTime]::Parse($cachedMap[$path].LastWriteTimeUtc).ToUniversalTime()
            $currentTime = [DateTime]::Parse($pdf.LastWriteTimeUtc).ToUniversalTime()
            if ($currentTime -gt $cachedTime) {
                $changes.Modified += $pdf
            }
        }
    }

    # Find deleted PDFs
    foreach ($pdf in $CachedPdfs) {
        $path = $pdf.Path
        if (-not $currentMap.ContainsKey($path)) {
            $changes.Deleted += $pdf
        }
    }

    return $changes
}

function Get-LatestPdfTimeUtc {
    <#
    # PURPOSE: Return the latest PDF modification time in UTC with incremental change detection.
    # DEPENDENCIES: pdf_root directory from config, optional cache.
    # MODIFICATION NOTES: Uses cache if available, performs incremental scan when possible.
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string]$PdfRoot,
        [Parameter(Mandatory = $false)]
        [string]$CachePath = $null,
        [Parameter(Mandatory = $false)]
        [int]$CacheTTLMinutes = 30
    )

    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    # Try to use cache first
    if ($CachePath) {
        $cachedPdfs = Get-CachedPdfList -CachePath $CachePath -PdfRoot $PdfRoot -CacheTTLMinutes $CacheTTLMinutes
        if ($null -ne $cachedPdfs -and $cachedPdfs.Count -gt 0) {
            # Perform incremental scan - only check cached PDFs and scan for new ones
            Write-DiagnosticLog -Message "Performing incremental PDF scan" -Data @{ 
                cached_pdf_count = $cachedPdfs.Count
                pdf_root = $PdfRoot
            }
            
            # Check cached PDFs for modifications (faster than full scan)
            $currentPdfs = @()
            $checkedCount = 0
            foreach ($cachedPdf in $cachedPdfs) {
                $pdfPath = $cachedPdf.Path
                if (Test-Path -LiteralPath $pdfPath) {
                    $fileInfo = Get-Item -LiteralPath $pdfPath -ErrorAction SilentlyContinue
                    if ($fileInfo) {
                        $currentPdfs += @{
                            Path = $fileInfo.FullName
                            LastWriteTimeUtc = $fileInfo.LastWriteTimeUtc.ToString("o")
                        }
                        $checkedCount++
                    }
                }
            }
            
            # Scan for new PDFs (only if directory structure might have changed)
            # This is still faster than full recursive scan since we skip known PDFs
            $knownPaths = @{}
            foreach ($pdf in $currentPdfs) {
                $knownPaths[$pdf.Path] = $true
            }
            
            # Quick scan for new PDFs in top-level and immediate subdirectories
            $newPdfs = Get-ChildItem -Path $PdfRoot -Filter "*.pdf" -File -ErrorAction SilentlyContinue
            foreach ($pdf in $newPdfs) {
                if (-not $knownPaths.ContainsKey($pdf.FullName)) {
                    $currentPdfs += @{
                        Path = $pdf.FullName
                        LastWriteTimeUtc = $pdf.LastWriteTimeUtc.ToString("o")
                    }
                }
            }
            
            # Detect changes
            $changes = Get-PdfChanges -CachedPdfs $cachedPdfs -CurrentPdfs $currentPdfs
            
            # Update cache if there are changes
            if ($changes.New.Count -gt 0 -or $changes.Modified.Count -gt 0 -or $changes.Deleted.Count -gt 0) {
                Write-DiagnosticLog -Message "PDF changes detected" -Data @{ 
                    new_count = $changes.New.Count
                    modified_count = $changes.Modified.Count
                    deleted_count = $changes.Deleted.Count
                }
                Save-CachedPdfList -CachePath $CachePath -PdfList $currentPdfs
            }
            
            # Find latest modification time
            if ($currentPdfs.Count -gt 0) {
                $latest = $currentPdfs | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
                if ($null -ne $latest) {
                    $stopwatch.Stop()
                    if ($EnableProfiling) {
                        Write-DiagnosticLog -Message "Get-LatestPdfTimeUtc (incremental)" -Data @{ 
                            duration_ms = $stopwatch.ElapsedMilliseconds
                            pdf_count = $currentPdfs.Count
                            used_cache = $true
                            checked_count = $checkedCount
                        }
                    }
                    return [DateTime]::Parse($latest.LastWriteTimeUtc).ToUniversalTime()
                }
            }
        }
    }

    # Full scan if cache unavailable or invalid
    Write-DiagnosticLog -Message "Performing full PDF scan" -Data @{ pdf_root = $PdfRoot }
    $pdfs = Get-ChildItem -Path $PdfRoot -Filter "*.pdf" -Recurse -File -ErrorAction SilentlyContinue
    
    if ($null -eq $pdfs -or $pdfs.Count -eq 0) {
        $stopwatch.Stop()
        if ($EnableProfiling) {
            Write-DiagnosticLog -Message "Get-LatestPdfTimeUtc (no PDFs)" -Data @{ 
                duration_ms = $stopwatch.ElapsedMilliseconds
                pdf_count = 0
            }
        }
        return $null
    }

    # Cache results for next run
    if ($CachePath) {
        $pdfList = $pdfs | ForEach-Object {
            @{
                Path = $_.FullName
                LastWriteTimeUtc = $_.LastWriteTimeUtc.ToString("o")
            }
        }
        Save-CachedPdfList -CachePath $CachePath -PdfList $pdfList
    }

    $latest = $pdfs | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    $stopwatch.Stop()
    if ($EnableProfiling) {
        Write-DiagnosticLog -Message "Get-LatestPdfTimeUtc (full scan)" -Data @{ 
            duration_ms = $stopwatch.ElapsedMilliseconds
            pdf_count = $pdfs.Count
            used_cache = $false
        }
    }
    if ($null -eq $latest) { return $null }
    return $latest.LastWriteTimeUtc
}

function Get-State {
    <#
    # PURPOSE: Read the last run state from disk.
    # DEPENDENCIES: State file path.
    # MODIFICATION NOTES: Returns hashtable or empty.
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string]$StatePath
    )

    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    if (-not (Test-Path -LiteralPath $StatePath)) {
        $stopwatch.Stop()
        Write-DiagnosticLog -Message "State file not found" -Data @{ state_path = $StatePath }
        if ($EnableProfiling) {
            Write-DiagnosticLog -Message "Get-State (not found)" -Data @{ 
                duration_ms = $stopwatch.ElapsedMilliseconds
            }
        }
        return @{}
    }
    $raw = Get-Content -LiteralPath $StatePath -Raw
    if (-not $raw) {
        $stopwatch.Stop()
        Write-DiagnosticLog -Message "State file empty" -Data @{ state_path = $StatePath }
        if ($EnableProfiling) {
            Write-DiagnosticLog -Message "Get-State (empty)" -Data @{ 
                duration_ms = $stopwatch.ElapsedMilliseconds
            }
        }
        return @{}
    }
    try {
        $stateObj = ($raw | ConvertFrom-Json)
        # Convert PSCustomObject to hashtable for consistent access
        $stateHash = @{}
        if ($null -ne $stateObj) {
            $stateObj.PSObject.Properties | ForEach-Object {
                $stateHash[$_.Name] = $_.Value
            }
        }
        $stopwatch.Stop()
        Write-DiagnosticLog -Message "State file parsed" -Data @{ 
            state_path = $StatePath
            state_type = $stateObj.GetType().FullName
            has_last_run_utc = $stateHash.ContainsKey("last_run_utc")
        }
        if ($EnableProfiling) {
            Write-DiagnosticLog -Message "Get-State" -Data @{ 
                duration_ms = $stopwatch.ElapsedMilliseconds
                file_size_bytes = $raw.Length
            }
        }
        return $stateHash
    } catch {
        $stopwatch.Stop()
        Write-DiagnosticLog -Message "State file parse error" -Data @{ 
            state_path = $StatePath
            error = $_.Exception.Message
        } -Level "ERROR"
        if ($EnableProfiling) {
            Write-DiagnosticLog -Message "Get-State (error)" -Data @{ 
                duration_ms = $stopwatch.ElapsedMilliseconds
                error = $_.Exception.Message
            }
        }
        return @{}
    }
}

function Save-State {
    <#
    # PURPOSE: Persist last run state to disk with backup.
    # DEPENDENCIES: State file path.
    # MODIFICATION NOTES: Creates backup before writing, writes JSON state.
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string]$StatePath,
        [Parameter(Mandatory = $true)]
        [DateTime]$LastRunUtc
    )

    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $writeDuration = 0

    # Use atomic write: write to temp file, then rename
    $tempPath = "$StatePath.tmp"
    $state = @{ last_run_utc = $LastRunUtc.ToString("o") }
    $writeStopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        # Write to temporary file first
        $state | ConvertTo-Json | Set-Content -LiteralPath $tempPath
        $writeStopwatch.Stop()
        $writeDuration = $writeStopwatch.ElapsedMilliseconds
        
        # Atomic rename (replaces existing file atomically on Windows)
        Move-Item -LiteralPath $tempPath -Destination $StatePath -Force
        $stopwatch.Stop()
        Write-DiagnosticLog -Message "State file written (atomic)" -Data @{ 
            state_path = $StatePath
            last_run_utc = $LastRunUtc.ToString("o")
        }
        if ($EnableProfiling) {
            Write-DiagnosticLog -Message "Save-State" -Data @{ 
                duration_ms = $stopwatch.ElapsedMilliseconds
                write_duration_ms = $writeDuration
                file_size_bytes = ($state | ConvertTo-Json).Length
                method = "atomic"
            }
        }
    } catch {
        $writeStopwatch.Stop()
        $stopwatch.Stop()
        # Clean up temp file if it exists
        if (Test-Path -LiteralPath $tempPath) {
            Remove-Item -LiteralPath $tempPath -ErrorAction SilentlyContinue
        }
        if ($EnableProfiling) {
            Write-DiagnosticLog -Message "Save-State (error)" -Data @{ 
                duration_ms = $stopwatch.ElapsedMilliseconds
                error = $_.Exception.Message
            }
        }
        throw
    }
}

# PURPOSE: Rotate diagnostic log if it exceeds size limit with retention policy.
# DEPENDENCIES: Diagnostic log path, configurable size limit and retention count.
# MODIFICATION NOTES: Archives old log, enforces retention policy (max 5 archived logs).
function Invoke-DiagnosticLogRotation {
    param(
        [Parameter(Mandatory = $true)]
        [string]$LogPath,
        [Parameter(Mandatory = $false)]
        [long]$MaxSizeMB = 10,
        [Parameter(Mandatory = $false)]
        [int]$MaxArchivedLogs = 5
    )

    if (-not (Test-Path -LiteralPath $LogPath)) {
        return
    }

    $logFile = Get-Item -LiteralPath $LogPath -ErrorAction SilentlyContinue
    if ($null -eq $logFile) {
        return
    }

    $maxSizeBytes = $MaxSizeMB * 1MB
    if ($logFile.Length -gt $maxSizeBytes) {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $archivePath = "$LogPath.$timestamp"
        $logDir = Split-Path -Parent $LogPath
        $logName = Split-Path -Leaf $LogPath
        
        try {
            # Rotate current log
            Move-Item -LiteralPath $LogPath -Destination $archivePath -Force
            
            # Enforce retention policy: keep only the most recent MaxArchivedLogs
            $archivedLogs = Get-ChildItem -Path $logDir -Filter "$logName.*" -File -ErrorAction SilentlyContinue | 
                Sort-Object LastWriteTime -Descending
            
            if ($archivedLogs.Count -gt $MaxArchivedLogs) {
                $logsToDelete = $archivedLogs | Select-Object -Skip $MaxArchivedLogs
                foreach ($oldLog in $logsToDelete) {
                    try {
                        Remove-Item -LiteralPath $oldLog.FullName -Force -ErrorAction SilentlyContinue
                    } catch {
                        # Ignore deletion errors for old logs
                    }
                }
            }
            
            # Log rotation event (to new log file)
            if ($script:DiagnosticLogPath) {
                $rotationData = @{
                    archive_path = $archivePath
                    original_size_mb = [math]::Round($logFile.Length / 1MB, 2)
                    archived_logs_count = $archivedLogs.Count
                    deleted_logs_count = if ($logsToDelete) { $logsToDelete.Count } else { 0 }
                }
                Write-DiagnosticLog -Message "Diagnostic log rotated" -Data $rotationData
            }
        } catch {
            # Can't use Write-DiagnosticLog here since log was moved, write to console if diagnostic mode
            if ($Diagnostic) {
                Write-Host "DIAGNOSTIC: Log rotation failed: $($_.Exception.Message)" -ForegroundColor Yellow
            }
        }
    }
}

# PURPOSE: Validate Python runtime availability.
# DEPENDENCIES: Python in system PATH.
# MODIFICATION NOTES: Returns $true if Python is available, $false otherwise.
function Test-PythonAvailable {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-DiagnosticLog -Message "Python runtime available" -Data @{ version = $pythonVersion }
            return $true
        }
    } catch {
        Write-DiagnosticLog -Message "Python runtime check failed" -Data @{ error = $_.Exception.Message } -Level "ERROR"
    }
    return $false
}

# PURPOSE: Validate template files exist.
# DEPENDENCIES: Config loaded, vault_root accessible.
# MODIFICATION NOTES: Returns $true if all templates exist, $false otherwise.
function Test-TemplatesExist {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$Config
    )
    
    $vaultRoot = $Config.vault_root
    $templateSource = Join-Path $vaultRoot $Config.templates.source_note
    $templateEntity = Join-Path $vaultRoot $Config.templates.entity_note
    
    $allExist = $true
    $missing = @()
    
    if (-not (Test-Path -LiteralPath $templateSource)) {
        $allExist = $false
        $missing += $templateSource
    }
    
    if (-not (Test-Path -LiteralPath $templateEntity)) {
        $allExist = $false
        $missing += $templateEntity
    }
    
    if (-not $allExist) {
        Write-DiagnosticLog -Message "Template files missing" -Data @{ missing_templates = $missing } -Level "ERROR"
    } else {
        Write-DiagnosticLog -Message "Template files validated" -Data @{ 
            source_template = $templateSource
            entity_template = $templateEntity
        }
    }
    
    return $allExist
}

# PURPOSE: Validate write permissions on vault directories.
# DEPENDENCIES: Config loaded, vault_root accessible.
# MODIFICATION NOTES: Returns $true if write access confirmed, $false otherwise.
function Test-VaultWriteAccess {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$Config
    )
    
    $vaultRoot = $Config.vault_root
    
    if (-not (Test-Path -LiteralPath $vaultRoot)) {
        Write-DiagnosticLog -Message "Vault root does not exist" -Data @{ vault_root = $vaultRoot } -Level "ERROR"
        return $false
    }
    
    try {
        $testFile = Join-Path $vaultRoot ".write_test"
        "test" | Set-Content -LiteralPath $testFile -ErrorAction Stop
        Remove-Item -LiteralPath $testFile -ErrorAction SilentlyContinue
        Write-DiagnosticLog -Message "Vault write access confirmed" -Data @{ vault_root = $vaultRoot }
        return $true
    } catch {
        Write-DiagnosticLog -Message "Vault write access denied" -Data @{ 
            vault_root = $vaultRoot
            error = $_.Exception.Message
        } -Level "ERROR"
        return $false
    }
}

# PURPOSE: Run all pre-flight validations and generate summary report.
# DEPENDENCIES: All validation functions, config path, script directory.
# MODIFICATION NOTES: Returns hashtable with validation results and summary.
function Invoke-PreflightValidation {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ConfigPath,
        [Parameter(Mandatory = $true)]
        [string]$ScriptDir
    )
    
    $results = @{
        PythonAvailable = $false
        ConfigExists = $false
        ConfigValid = $false
        IngestScriptExists = $false
        TemplatesExist = $false
        VaultWriteAccess = $false
        AllPassed = $false
        Errors = @()
        Warnings = @()
        Summary = ""
    }
    
    $ingestPath = Join-Path $ScriptDir "ingest_pdfs.py"
    
    # Check Python availability
    $results.PythonAvailable = Test-PythonAvailable
    if (-not $results.PythonAvailable) {
        $results.Errors += "Python runtime not available. Resolution: Install Python and ensure it's in your system PATH."
    } else {
        try {
            $pythonVersion = python --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                $results.Summary += "[OK] Python runtime: $pythonVersion`n"
            }
        } catch {
            # Already logged by Test-PythonAvailable
        }
    }
    
    # Check config file exists
    $results.ConfigExists = Test-Path -LiteralPath $ConfigPath
    if (-not $results.ConfigExists) {
        $results.Errors += "Configuration file not found: $ConfigPath. Resolution: Ensure ingest_config.json exists in the scripts directory."
    } else {
        $results.Summary += "[OK] Configuration file found: $ConfigPath`n"
    }
    
    # Load and validate config
    if ($results.ConfigExists) {
        try {
            $configContent = Get-Content -LiteralPath $ConfigPath -Raw
            if (-not $configContent) {
                $results.Errors += "Configuration file is empty. Resolution: Restore ingest_config.json from backup or recreate it."
                $results.ConfigValid = $false
            } else {
                $configObj = $configContent | ConvertFrom-Json
                # Convert PSCustomObject to hashtable for consistent access
                $config = @{}
                $configObj.PSObject.Properties | ForEach-Object {
                    $config[$_.Name] = $_.Value
                }
                
                # Validate required config keys
                $requiredKeys = @("vault_root", "pdf_root", "source_notes_dir", "templates")
                $missingKeys = @()
                foreach ($key in $requiredKeys) {
                    if (-not $config.PSObject.Properties.Name -contains $key) {
                        $missingKeys += $key
                    }
                }
                
                if ($missingKeys.Count -gt 0) {
                    $results.Errors += "Missing required config keys: $($missingKeys -join ', '). Resolution: Add missing keys to ingest_config.json."
                    $results.ConfigValid = $false
                } else {
                    # Validate paths don't contain dangerous patterns
                    $pathKeys = @("vault_root", "pdf_root")
                    $invalidPaths = @()
                    foreach ($key in $pathKeys) {
                        $pathValue = $config.$key
                        if ($pathValue -match '\.\.' -or $pathValue -match '^[A-Z]:\\$') {
                            $invalidPaths += "$key = $pathValue"
                        }
                    }
                    
                    if ($invalidPaths.Count -gt 0) {
                        $results.Errors += "Invalid paths in config: $($invalidPaths -join ', '). Resolution: Fix path values in ingest_config.json."
                        $results.ConfigValid = $false
                    } else {
                        $results.ConfigValid = $true
                        $results.Summary += "[OK] Configuration valid`n"
                        
                        # Check templates
                        $results.TemplatesExist = Test-TemplatesExist -Config $config
                        if (-not $results.TemplatesExist) {
                            $vaultRoot = $config.vault_root
                            $templateSource = Join-Path $vaultRoot $config.templates.source_note
                            $templateEntity = Join-Path $vaultRoot $config.templates.entity_note
                            $missing = @()
                            if (-not (Test-Path -LiteralPath $templateSource)) {
                                $missing += $templateSource
                            }
                            if (-not (Test-Path -LiteralPath $templateEntity)) {
                                $missing += $templateEntity
                            }
                            $results.Errors += "Template files missing: $($missing -join ', '). Resolution: Ensure template files exist in the Templates directory."
                        } else {
                            $results.Summary += "[OK] Template files validated`n"
                        }
                        
                        # Check vault write access
                        $results.VaultWriteAccess = Test-VaultWriteAccess -Config $config
                        if (-not $results.VaultWriteAccess) {
                            $results.Errors += "Vault write access denied. Resolution: Check file permissions on vault directory: $($config.vault_root)"
                        } else {
                            $results.Summary += "[OK] Vault write access confirmed`n"
                        }
                    }
                }
            }
        } catch {
            $results.Errors += "Failed to load or validate configuration: $($_.Exception.Message). Resolution: Check JSON syntax and required fields in ingest_config.json."
            $results.ConfigValid = $false
        }
    }
    
    # Check ingestion script exists
    $results.IngestScriptExists = Test-Path -LiteralPath $ingestPath
    if (-not $results.IngestScriptExists) {
        $results.Errors += "Ingestion script not found: $ingestPath. Resolution: Ensure ingest_pdfs.py exists in the scripts directory."
    } else {
        $results.Summary += "[OK] Ingestion script found: $ingestPath`n"
    }
    
    # Determine overall status
    $results.AllPassed = $results.PythonAvailable -and $results.ConfigExists -and $results.ConfigValid -and $results.IngestScriptExists -and $results.TemplatesExist -and $results.VaultWriteAccess
    
    return $results
}

# PURPOSE: Display validation summary report.
# DEPENDENCIES: Validation results hashtable.
# MODIFICATION NOTES: Formats and displays summary with actionable error messages.
function Show-ValidationSummary {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$ValidationResults
    )
    
    if ($ValidationResults.AllPassed) {
        if ($Diagnostic) {
            Write-Host "`n=== PRE-FLIGHT VALIDATION SUMMARY ===" -ForegroundColor Green
            Write-Host $ValidationResults.Summary -ForegroundColor Green
            Write-Host "All checks passed. System ready for ingestion.`n" -ForegroundColor Green
        }
        Write-DiagnosticLog -Message "Pre-flight validation passed" -Data @{ summary = $ValidationResults.Summary }
    } else {
        if ($Diagnostic) {
            Write-Host "`n=== PRE-FLIGHT VALIDATION SUMMARY ===" -ForegroundColor Red
            Write-Host "Validation FAILED. The following issues were found:`n" -ForegroundColor Red
            
            if ($ValidationResults.Summary) {
                Write-Host "Passed checks:" -ForegroundColor Yellow
                Write-Host $ValidationResults.Summary -ForegroundColor Yellow
                Write-Host ""
            }
            
            Write-Host "Errors:" -ForegroundColor Red
            foreach ($errorMsg in $ValidationResults.Errors) {
                Write-Host "  ✗ $errorMsg" -ForegroundColor Red
            }
            Write-Host ""
        }
        
        Write-DiagnosticLog -Message "Pre-flight validation failed" -Data @{ 
            errors = $ValidationResults.Errors
            summary = $ValidationResults.Summary
        } -Level "ERROR"
    }
    
    return $ValidationResults.AllPassed
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$configPath = Join-Path $scriptDir "ingest_config.json"
$statePath = Join-Path $scriptDir "ingest_state.json"
$ingestPath = Join-Path $scriptDir "ingest_pdfs.py"
$pdfCachePath = Join-Path $scriptDir "ingest_pdf_cache.json"

# Initialize diagnostic logging
if ($Diagnostic) {
    if ($LogPath) {
        $script:DiagnosticLogPath = $LogPath
    } else {
        $script:DiagnosticLogPath = Join-Path $scriptDir "ingest_diagnostic.log"
    }
    
    # Rotate log if needed (before first write)
    Invoke-DiagnosticLogRotation -LogPath $script:DiagnosticLogPath -MaxSizeMB 10 -MaxArchivedLogs 5
    
    Write-DiagnosticLog -Message "Diagnostic mode enabled" -Data @{ log_path = $script:DiagnosticLogPath }
}

# Pre-flight validation with summary report
Write-DiagnosticLog -Message "Starting pre-flight validation" -Data @{}

$validationResults = Invoke-PreflightValidation -ConfigPath $configPath -ScriptDir $scriptDir

if (-not (Show-ValidationSummary -ValidationResults $validationResults)) {
    exit 1
}

# Load config for use (already validated)
try {
    $configContent = Get-Content -LiteralPath $configPath -Raw
    $config = $configContent | ConvertFrom-Json
    Write-DiagnosticLog -Message "Configuration loaded" -Data @{ config_path = $configPath }
} catch {
    $errorMsg = "Failed to load configuration after validation: $($_.Exception.Message)"
    Write-DiagnosticLog -Message $errorMsg -Level "ERROR"
    if ($Diagnostic) {
        Write-Host "DIAGNOSTIC: $errorMsg" -ForegroundColor Red
    }
    exit 1
}

$pdfRoot = $config.pdf_root

Write-DiagnosticLog -Message "Configuration loaded" -Data @{ pdf_root = $pdfRoot; config_path = $configPath }

# Scan PDFs with error handling
try {
    $pdfFiles = Get-ChildItem -Path $pdfRoot -Filter "*.pdf" -Recurse -File -ErrorAction Stop
    $pdfCount = if ($pdfFiles) { $pdfFiles.Count } else { 0 }
    Write-DiagnosticLog -Message "PDF scan completed" -Data @{ pdf_count = $pdfCount; pdf_root = $pdfRoot }
} catch {
    $errorMsg = "Failed to scan PDF directory: $($_.Exception.Message)"
    Write-DiagnosticLog -Message $errorMsg -Level "ERROR"
    if ($Diagnostic) {
        Write-Host "DIAGNOSTIC: $errorMsg" -ForegroundColor Red
    }
    # Continue anyway - Get-LatestPdfTimeUtc will handle empty directory
}

$latestPdfTime = Get-LatestPdfTimeUtc -PdfRoot $pdfRoot -CachePath $pdfCachePath -CacheTTLMinutes 30
if ($null -eq $latestPdfTime) {
    Write-DiagnosticLog -Message "No PDFs found, exiting" -Data @{ pdf_root = $pdfRoot }
    if ($Diagnostic) {
        Write-Host "DIAGNOSTIC: No PDFs found in $pdfRoot" -ForegroundColor Yellow
    }
    exit 0
}

Write-DiagnosticLog -Message "Latest PDF time determined" -Data @{ latest_pdf_time_utc = $latestPdfTime.ToString("o") }

$state = Get-State -StatePath $statePath
$lastRunUtc = $null
if ($null -ne $state -and $state.ContainsKey("last_run_utc")) {
    $lastRunUtc = [DateTime]::Parse($state["last_run_utc"]).ToUniversalTime()
    Write-DiagnosticLog -Message "State file read" -Data @{ 
        state_path = $statePath
        last_run_utc = $lastRunUtc.ToString("o")
        state_exists = $true
    }
} else {
    Write-DiagnosticLog -Message "State file missing or invalid" -Data @{ 
        state_path = $statePath
        state_exists = (Test-Path -LiteralPath $statePath)
    }
}

$shouldIngest = $null -eq $lastRunUtc -or $latestPdfTime -gt $lastRunUtc
Write-DiagnosticLog -Message "Ingestion decision" -Data @{ 
    should_ingest = $shouldIngest
    last_run_utc = if ($lastRunUtc) { $lastRunUtc.ToString("o") } else { $null }
    latest_pdf_time_utc = $latestPdfTime.ToString("o")
    reason = if ($null -eq $lastRunUtc) { "no_previous_run" } elseif ($latestPdfTime -gt $lastRunUtc) { "pdfs_newer_than_last_run" } else { "no_new_pdfs" }
}

if ($shouldIngest) {
    if ($Diagnostic) {
        Write-Host "DIAGNOSTIC: Triggering ingestion (reason: $($shouldIngest))" -ForegroundColor Green
    }
    Write-DiagnosticLog -Message "Starting ingestion" -Data @{ ingest_script = $ingestPath }
    
    $ingestStopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $timeoutSeconds = 300  # 5 minutes default timeout
    
    try {
        # Create a job to run Python with timeout
        $job = Start-Job -ScriptBlock {
            param($scriptPath)
            $output = & python $scriptPath 2>&1
            $exitCode = $LASTEXITCODE
            return @{
                Output = $output
                ExitCode = $exitCode
            }
        } -ArgumentList $ingestPath
        
        # Wait for job with timeout
        $jobCompleted = Wait-Job -Job $job -Timeout $timeoutSeconds
        
        if (-not $jobCompleted) {
            $ingestStopwatch.Stop()
            Stop-Job -Job $job
            Remove-Job -Job $job -Force
            $errorMsg = "Ingestion timed out after $timeoutSeconds seconds"
            Write-DiagnosticLog -Message $errorMsg -Level "ERROR"
            if ($Diagnostic) {
                Write-Host "DIAGNOSTIC: $errorMsg" -ForegroundColor Red
            }
            if ($EnableProfiling) {
                Write-DiagnosticLog -Message "Ingestion (timeout)" -Data @{ 
                    duration_ms = $ingestStopwatch.ElapsedMilliseconds
                    timeout_seconds = $timeoutSeconds
                }
            }
            throw New-Object System.TimeoutException($errorMsg)
        }
        
        $jobResult = Receive-Job -Job $job
        Remove-Job -Job $job -Force
        $ingestStopwatch.Stop()
        
        if ($jobResult -is [hashtable]) {
            $ingestResult = $jobResult.Output
            $ingestExitCode = $jobResult.ExitCode
        } else {
            # Fallback for older PowerShell versions
            $ingestResult = $jobResult
            $ingestExitCode = $LASTEXITCODE
        }
        
        if ($null -eq $ingestExitCode) {
            $ingestExitCode = 0  # Assume success if no exit code
        }
        
        $ingestDuration = $ingestStopwatch.Elapsed.TotalSeconds
        
        Write-DiagnosticLog -Message "Ingestion completed" -Data @{ 
            exit_code = $ingestExitCode
            duration_seconds = $ingestDuration
            duration_ms = $ingestStopwatch.ElapsedMilliseconds
            stdout_length = if ($ingestResult) { $ingestResult.Length } else { 0 }
        }
        
        if ($Diagnostic) {
            if ($ingestExitCode -eq 0) {
                Write-Host "DIAGNOSTIC: Ingestion succeeded (exit code: $ingestExitCode, duration: $([math]::Round($ingestDuration, 2))s)" -ForegroundColor Green
            } else {
                Write-Host "DIAGNOSTIC: Ingestion failed (exit code: $ingestExitCode)" -ForegroundColor Red
                if ($ingestResult) {
                    Write-Host "DIAGNOSTIC: Output: $($ingestResult -join "`n")" -ForegroundColor Yellow
                }
            }
        }
        
        Save-State -StatePath $statePath -LastRunUtc ([DateTime]::UtcNow)
        Write-DiagnosticLog -Message "State saved" -Data @{ 
            state_path = $statePath
            new_last_run_utc = ([DateTime]::UtcNow).ToString("o")
        }
    } catch {
        Write-DiagnosticLog -Message "Ingestion error" -Data @{ 
            error = $_.Exception.Message
            error_type = $_.Exception.GetType().FullName
        } -Level "ERROR"
        if ($Diagnostic) {
            Write-Host "DIAGNOSTIC: Ingestion error: $($_.Exception.Message)" -ForegroundColor Red
        }
        throw
    }
} else {
    if ($Diagnostic) {
        Write-Host "DIAGNOSTIC: Skipping ingestion (no new PDFs since last run)" -ForegroundColor Cyan
    }
}
