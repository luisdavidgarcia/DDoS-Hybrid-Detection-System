# Create the directory for Nginx files
$nginxDir = "../nginx/www"
if (-not (Test-Path $nginxDir)) {
    New-Item -Path $nginxDir -ItemType Directory
}

# Generate a small HTML file (1KB)
$smallHtmlContent = "<html><body><h1>Small File</h1></body></html>"
$smallFilePath = Join-Path $nginxDir "small.html"
$smallHtmlContent | Out-File -FilePath $smallFilePath -Encoding utf8

# Generate a medium file (1MB)
$mediumFilePath = Join-Path $nginxDir "medium.html"
$mediumContent = New-Object byte[] (1MB)
[byte]0 | ForEach-Object { $mediumContent }  # Fill the file with zeros
[System.IO.File]::WriteAllBytes($mediumFilePath, $mediumContent)

# List the created files
Write-Host "Files created in the nginx/www directory:"
Get-ChildItem -Path $nginxDir | Format-Table Name, Length