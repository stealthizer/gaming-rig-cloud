# 372.90 are the last known drivers to work with GRID
$url = "http://us.download.nvidia.com/Windows/372.90/372.90-desktop-win8-win7-64bit-international-whql.exe"
$output = "$PSScriptRoot\372.90-desktop-win8-win7-64bit-international-whql.exe"
$start_time = Get-Date

$wc = New-Object System.Net.WebClient
$wc.DownloadFile($url, $output)
Move-Item  "$PSScriptRoot\372.90-desktop-win8-win7-64bit-international-whql.exe" C:\utils\
Write-Output "Time taken: $((Get-Date).Subtract($start_time).Seconds) second(s)"
Write-Output "unpacking nvidia driver"
# check beyond this point
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) { Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs; exit }
$command = "c:\utils\372.90-desktop-win8-win7-64bit-international-whql.exe -s"
Invoke-Expression -Command $command