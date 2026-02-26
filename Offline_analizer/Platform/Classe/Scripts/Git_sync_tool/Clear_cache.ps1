if (Test-Path -Path $env:LOCALAPPDATA\Temp\gen_py){
    Remove-Item -Recurse -path $env:LOCALAPPDATA\Temp\gen_py
    Write-Host "CanOE local python cache cleared."
}
else {
    Write-Host "Canoe local python cache already cleared."
}
