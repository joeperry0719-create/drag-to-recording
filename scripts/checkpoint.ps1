param(
    [Parameter(Mandatory=$true)]
    [string]$Message
)

$ErrorActionPreference = "Stop"
git status
git diff --stat
git add .
git commit -m $Message
