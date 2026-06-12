param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$Root = $PSScriptRoot
$VenvPython = Join-Path $Root "venv\Scripts\python.exe"
$Python = if (Test-Path $VenvPython) { $VenvPython } else { "python" }

& $Python (Join-Path $Root "main.py") @Args
