$url = "http://rzr.to/surround-pc-download"
$output = "$PSScriptRoot\RazerSurroundInstaller.exe"
$start_time = Get-Date
Write-Output "Downloading Razer Surround Driver"

$wc = New-Object System.Net.WebClient
$wc.DownloadFile($url, $output)
Move-Item  "$PSScriptRoot\RazerSurroundInstaller.exe" C:\utils\
Write-Output "Time taken: $((Get-Date).Subtract($start_time).Seconds) second(s)"