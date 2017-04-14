Write-Output "Downloading nvidia drivers"
$nvidia_version = "372.90"
$url = "http://es.download.nvidia.com/Windows/$($nvidia_version)/$($nvidia_version)-desktop-win10-32bit-international-whql.exe"
$output = "$PSScriptRoot\nvidia_driver-$($nvidia_version).exe"
$start_time = Get-Date

(New-Object System.Net.WebClient).DownloadFile($url, $output)
Write-Output "Time taken: $((Get-Date).Subtract($start_time).Seconds) second(s)"
