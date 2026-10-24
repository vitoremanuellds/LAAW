# Thin wrapper for the LAAW CLI (requires Python 3 on PATH).
# Resolves the repo root from its own location so `laaw` works from any cwd.
$RepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$env:PYTHONPATH = "$RepoRoot" + $(if ($env:PYTHONPATH) { ";" + $env:PYTHONPATH } else { "" })
if (Get-Command py -ErrorAction SilentlyContinue) {
    py -m laaw @args
} else {
    python -m laaw @args
}
