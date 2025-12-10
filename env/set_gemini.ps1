param(
  [Parameter(Mandatory=$true)][string]$API_KEY,
  [string]$MODEL = "gemini-2.0-flash-lite"
)

# Kiem tra key cu trong phien hien tai
$OldKey = $env:GOOGLE_API_KEY
if ($OldKey) {
    $MaskedOld = $OldKey.Substring(0, [math]::Min(100, $OldKey.Length)) + "..."
    Write-Output "Key cu dang duoc su dung: $MaskedOld"
} else {
    Write-Output "Chua co API Key nao duoc thiet lap."
}

# Cap nhat ENV (User Scope)
[Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", $API_KEY, "User")
[Environment]::SetEnvironmentVariable("GEMINI_MODEL", $MODEL, "User")

# Cap nhat cho phien hien tai
$env:GOOGLE_API_KEY = $API_KEY
$env:GEMINI_MODEL = $MODEL

Write-Output "Da cap nhat API Key moi."
Write-Output "Model dang su dung: $MODEL"
Write-Output "Neu dung VS Code, hay mo terminal moi de nhan ENV moi."
Write-Output "He thong chi doc GEMINI_MODEL tu ENV; Python se bao loi neu thieu."
Write-Output "De doi model, chay lai: .\env\set_gemini.ps1 -API_KEY \"API_KEY\" -MODEL \"gemini-2.5-flash\""
