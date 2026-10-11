# From the extracted Telecom_AI_Replay_V1 folder, run: .\run_windows.ps1
# Installs open-source UI dependencies if not already available; does not
# invoke any telecom model, LangSmith API, GCP, or hosted telemetry service.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    python -m venv .venv
}
& '.venv\Scripts\python.exe' -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
& '.venv\Scripts\python.exe' -m streamlit run app.py
