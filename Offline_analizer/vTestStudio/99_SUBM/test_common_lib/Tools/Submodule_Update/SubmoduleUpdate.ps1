<#
.SYNOPSIS
This script updates a submodule within a specific repository to a specific commit hash.

.Description
The Script executes steps needed to update a submodule within a git repository to a specific hash file.

Prerequisites:
  - The script shall be called from the Repository Root Directory
  - The Repository shall be in a proper state, before executing this script. This can be checked as follows:
    - From Repository Root: "git submodule update --init --recursive" shall be executed successfully without errors. 
	- From Repository Root: "git status" shall not show any modification. (Untracked files ok)

The script makes the following:
  - In the Submodule path: Update the submodule to the provided commit hash
  - In the Repository path: Stage the submodule commit change + commit
The script does not push the changes. If needed, this shall be done manually independent of this script. 

The User shall revise the stdout of the commands executed by the script, and double check they succeed without errors.
 

.PARAMETER submodulePath
The path to the directory of the submodule, relative to the Repository root.

.PARAMETER commitHash
The commit hash to which the submodule should be updated

.EXAMPLE
cd <Repository Root>
powershell <path\to\SubmoduleUpdate.ps1> -submodulePath <rel/path/to/submodule> -commitHash <commit-hash>
Updates the submodule to the provided commit-hash
#>

<#
  Copyright  (C) 2021-2021 Robert Bosch GmbH.\n
  The reproduction, distribution and utilization of this file as well as
  the communication of its contents to others without express authorization
  is prohibited.\n
  Offenders will be held liable for the payment of damages.\n
  All rights reserved in the event of the grant of a patent, utility model or design.
 
  File         SubmoduleUpdate.ps1
                                             
  Author       Ahmad Khalil (XC-DA/EET2)
  Date         22.04.2021
  Version      0.1

  History:      22.04.2021  Initial version
#>

param (
    [string] $submodulePath,
    [string] $commitHash
)

Write-Output "submodulePath=$submodulePath"
Write-Output "commitHash=$commitHash"
[Console]::Out.Flush()

if(-not $submodulePath -or -not $commitHash) {
	$(throw "Parameters -submodulePath and -commitHash are mandatory, please provide the values.")
}

Read-Host -Prompt "
Prerequisites:
  - The script shall be called from the Repository Root Directory
  - The Repository shall be in a proper state, before executing this script. This can be checked as follows:
    - From Repository Root: (git submodule update --init --recursive) shall be executed successfully without errors. 
    - From Repository Root: (git status) shall not show any modification. (Untracked files ok)
Please check the above prerequisites are satisfied, then press any key to continue or CTRL+C to quit"

Write-Output "updating submodule ..."
[Console]::Out.Flush()

$repoDir = $pwd
Write-Output "`ncd $submodulePath"; cd $submodulePath; if (-not $?) {Write-Output "Failed"; exit 1}
Write-Output "`ngit fetch --all"; git fetch --all; if (-not $?) {Write-Output "Failed";exit 1}
Write-Output "`ngit checkout $commitHash"; git checkout $commitHash; if (-not $?) {Write-Output "Failed";exit 1}
Write-Output "`ncd $repoDir"; cd $repoDir; if (-not $?) {Write-Output "Failed"; exit 1}
Write-Output "`ngit add $submodulePath"; git add $submodulePath; if (-not $?) {Write-Output "Failed"; exit 1}
Write-Output "`ngit commit -m ""Submodule ($submodulePath) is updated to commit hash: $commitHash"""; git commit -m "Submodule ($submodulePath) is updated to commit hash: $commitHash"; if (-not $?) {Write-Output "Failed"; exit 1}

exit 0