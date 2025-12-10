# Script xóa toàn bộ biến môi trường liên quan đến Gemini API

# Xóa biến môi trường trong User scope (tương đương xóa khỏi setx vĩnh viễn)
[Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", $null, "User")
[Environment]::SetEnvironmentVariable("GEMINI_MODEL", $null, "User")

# Xóa biến môi trường trong session hiện tại (cửa sổ đang mở)
$env:GOOGLE_API_KEY = $null
$env:GEMINI_MODEL = $null

Write-Output "Xoa thanh cong"