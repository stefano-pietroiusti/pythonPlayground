param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("dev", "qa", "prod")]
    [string]$Environment,

    [Parameter(Mandatory = $false)]
    [string]$DbtCommand = "build"   # build, run, test, compile, etc.
)

Write-Host "Starting dbt job for environment: $Environment"
Write-Host "Using dbt command: dbt $DbtCommand"

# Paths
$ProjectDir   = "armdsl"
$ProfilesPath = "armdsl\profiles"
$SourceProfile = Join-Path $ProfilesPath "profiles-$Environment.yml"
$ActiveProfile = Join-Path $ProfilesPath "profiles.yml"

# Validate profile exists
if (-not (Test-Path $SourceProfile)) {
    Write-Host "ERROR: Profile file not found: $SourceProfile"
    exit 99
}

# Copy correct profile into place
Copy-Item $SourceProfile $ActiveProfile -Force
Write-Host "Copied profile: $SourceProfile → $ActiveProfile"

# Activate venv if present
$VenvActivate = ".\venv\Scripts\Activate.ps1"
if (Test-Path $VenvActivate) {
    Write-Host "Activating Python virtual environment"
    . $VenvActivate
} else {
    Write-Host "WARNING: venv not found, assuming dbt is available globally"
}

# Run dbt
Write-Host "Running: dbt $DbtCommand --project-dir $ProjectDir --profiles-dir $ProfilesPath --target $Environment"
dbt $DbtCommand --project-dir $ProjectDir --profiles-dir $ProfilesPath --target $Environment
$DbtExitCode = $LASTEXITCODE

# Handle exit code
if ($DbtExitCode -ne 0) {
    Write-Host "dbt $DbtCommand FAILED with exit code $DbtExitCode"
    exit $DbtExitCode
} else {
    Write-Host "dbt $DbtCommand completed successfully"
    exit 0
}
