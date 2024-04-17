[CmdletBinding()]
Param(
    $pythonVersion = "3.11.9",
	$folder="Python-----($pythonVersion)",
	$dirpath = "C:\$folder",
    $pythonUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-amd64.exe",
    $pythonDownloadPath = "C:\$folder\python-$pythonVersion-amd64.exe",
    $pythonInstallDir = "C:\$folder\Python$pythonVersion"
)
echo "File doesn't exist. Creating now"
mkdir "$dirpath"
 
 
echo "GIVE USER AND PASSWORD ADMINISTRATOR ACCESS"
 
(New-Object Net.WebClient).DownloadFile($pythonUrl, $pythonDownloadPath)
& $pythonDownloadPath /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 TargetDir=$pythonInstallDir
Write-Host "Installing: "
 
for ($i = 0; $i -le 100; $i+=33) {
    $progress = ""
    switch ($i) {
        {$_ -lt 33} { $progress = "#####"; break }
        {$_ -lt 66} { $progress = "#############"; break }
        {$_ -lt 100} { $progress = "#######################"; break }
        default { $progress = "#######################"; break }
    }
    Write-Host -NoNewline -ForegroundColor Cyan ("`r{0,-25} ({1}%)" -f $progress, $i)
    Start-Sleep -Seconds 7
}
 
# Print 100% completion
Write-Host -ForegroundColor Cyan "`r#######################   (100%)"
 
echo "Installation completed"
echo "Please proceed with the package installer BAT."