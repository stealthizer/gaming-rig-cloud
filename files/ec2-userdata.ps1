<powershell>

Write-Output "Setting up Packer user"
cmd.exe /c net user /add packer G9HsM%?Lz*
cmd.exe /c net localgroup administrators packer /add
cmd.exe /c wmic useraccount where "name='packer'" set PasswordExpires=FALSE

Write-Output "Configure WinRM"
winrm quickconfig -q
winrm set winrm/config/winrs '@{MaxMemoryPerShellMB="300"}'
winrm set winrm/config '@{MaxTimeoutms="1800000"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
winrm set winrm/config/service/auth '@{Basic="true"}'

Write-Output "Configure firewal WinRM port"
netsh advfirewall firewall add rule name="WinRM 5985" protocol=TCP dir=in localport=5985 action=allow

Write-Output "Restart WinRM service"
Stop-Service WinRM
Set-Service WinRM -startuptype Automatic
Start-Service WinRM

Write-Output "Execution policy restrictions"
Set-ExecutionPolicy Unrestricted -Force

</powershell>