if (Get-SmbShare -Name "ADAS_Project") {
    Remove-SmbShare -Name 'ADAS_Project' -Force
    Write-Output "Remove Share "
}

