param($a)
$path = "$a"
$ArgumentLst = @("New-SmbShare -Path $path -Name 'ADAS_Project' -FullAccess 'Everyone'")
Start-Process powershell -verb runas -ArgumentList "-file $path\Platform\Classe\Scripts\CarMaker_scripts\remove_share.ps1"
Start-Process powershell -verb runas -ArgumentList $ArgumentLst
Write-Output "Shared $path"
