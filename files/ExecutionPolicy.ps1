
# Checking Execution Policy
#
write-output "Execution Policy PowerShell"

$cmdPolicy = (get-ExecutionPolicy)
$Policy = "Unrestricted"
If ( $cmdPolicy -ne $Policy) {
  write-output "Script Execution is disabled. Enabling it now"
  Set-ExecutionPolicy $Policy -Force
  } else {
    write-output "Execution Policy is $cmdPolicy"
  }