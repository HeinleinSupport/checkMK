# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
#
# Sign a Windows binary using Azure Artifact Signing via the ArtifactSigning
# PowerShell module (Install-Module -Name ArtifactSigning, https://www.powershellgallery.com/packages/ArtifactSigning).
#
# Prerequisites:
#   - ArtifactSigning PS module:  Install-Module -Name ArtifactSigning
#   - dotnet runtime (.NET 8):    shipped with Visual Studio 2022, or https://dotnet.microsoft.com/download/dotnet/8.0
#
# Required environment variables:
#   AZURE_ARTIFACT_SIGNING_ENDPOINT       e.g. https://neu.codesigning.azure.net
#   AZURE_ARTIFACT_SIGNING_ACCOUNT        Code signing account name
#   AZURE_ARTIFACT_SIGNING_PROFILE        Certificate profile name
#   AZURE_ARTIFACT_SIGNING_TENANT_ID      Azure AD tenant ID
#   AZURE_ARTIFACT_SIGNING_CLIENT_ID      Service principal client ID
#   AZURE_ARTIFACT_SIGNING_CLIENT_SECRET  Service principal client secret (sensitive)
[CmdletBinding()]
param([Parameter(Mandatory = $true)][string]$FilePath)

$ErrorActionPreference = 'Stop'

# The .NET 8 SDK installer places dotnet at this standard location and adds it to the
# system PATH. Add it explicitly here as a safety net for non-standard CI environments.
$dotnetDir = "C:\Program Files\dotnet"
if ((Test-Path $dotnetDir) -and ($env:PATH -notlike "*$dotnetDir*")) {
    $env:PATH += ";$dotnetDir"
}

Import-Module ArtifactSigning -ErrorAction Stop

foreach ($var in @('AZURE_ARTIFACT_SIGNING_ENDPOINT', 'AZURE_ARTIFACT_SIGNING_ACCOUNT',
        'AZURE_ARTIFACT_SIGNING_PROFILE', 'AZURE_ARTIFACT_SIGNING_TENANT_ID',
        'AZURE_ARTIFACT_SIGNING_CLIENT_ID', 'AZURE_ARTIFACT_SIGNING_CLIENT_SECRET')) {
    if (-not [Environment]::GetEnvironmentVariable($var)) {
        Write-Error "Required environment variable $var is not set"
    }
}

# Invoke-ArtifactSigning uses DefaultAzureCredential internally; map our prefixed
# vars to the standard Azure SDK names read by EnvironmentCredential.
$env:AZURE_TENANT_ID = $env:AZURE_ARTIFACT_SIGNING_TENANT_ID
$env:AZURE_CLIENT_ID = $env:AZURE_ARTIFACT_SIGNING_CLIENT_ID
$env:AZURE_CLIENT_SECRET = $env:AZURE_ARTIFACT_SIGNING_CLIENT_SECRET

try {
    Write-Host "Signing $FilePath with Azure Artifact Signing..."
    Invoke-ArtifactSigning `
        -Endpoint              $env:AZURE_ARTIFACT_SIGNING_ENDPOINT `
        -CodeSigningAccountName $env:AZURE_ARTIFACT_SIGNING_ACCOUNT `
        -CertificateProfileName $env:AZURE_ARTIFACT_SIGNING_PROFILE `
        -Files                 $FilePath `
        -FileDigest            SHA256 `
        -TimestampRfc3161      "http://timestamp.acs.microsoft.com" `
        -TimestampDigest       SHA256 `
        -ExcludeWorkloadIdentityCredential `
        -ExcludeManagedIdentityCredential `
        -ExcludeSharedTokenCacheCredential `
        -ExcludeVisualStudioCredential `
        -ExcludeVisualStudioCodeCredential `
        -ExcludeAzureCliCredential `
        -ExcludeAzurePowerShellCredential `
        -ExcludeInteractiveBrowserCredential
    Write-Host "Signed: $FilePath"
}
finally {
    Remove-Item Env:\AZURE_TENANT_ID     -ErrorAction SilentlyContinue
    Remove-Item Env:\AZURE_CLIENT_ID     -ErrorAction SilentlyContinue
    Remove-Item Env:\AZURE_CLIENT_SECRET -ErrorAction SilentlyContinue
}
