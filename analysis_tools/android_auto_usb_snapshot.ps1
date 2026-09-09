<#
.SYNOPSIS
Read a redacted Windows PnP snapshot for a Samsung/Google USB bench device.
.DESCRIPTION
Read-only. No driver changes, USB requests, phone commands, or file writes.
Instance suffixes, friendly names, container IDs, and location paths are omitted.
Hardware and compatible IDs are limited to standard USB VID/PID/interface/class
tokens. Output is JSON on stdout; select another VID for other manufacturers.
#>
[CmdletBinding()]
param(
    [ValidatePattern('^[0-9A-Fa-f]{4}$')]
    [string[]]$VendorId = @('04E8', '18D1')
)

$ErrorActionPreference = 'Stop'
$benchPattern = '^USB\\VID_(' + (($VendorId | ForEach-Object {
    [regex]::Escape($_)
}) -join '|') + ')&PID_[0-9A-F]{4}'
$benchDevices = @(Get-PnpDevice -PresentOnly | Where-Object {
    $_.InstanceId -match $benchPattern
})
$benchRows = @(foreach ($benchDevice in $benchDevices) {
    $benchProperties = @(Get-PnpDeviceProperty -InstanceId $benchDevice.InstanceId)
    $benchValues = @{}
    foreach ($benchProperty in $benchProperties) {
        $benchValues[$benchProperty.KeyName] = $benchProperty.Data
    }
    $benchIdentity = [regex]::Match(
        $benchDevice.InstanceId, 'VID_[0-9A-F]{4}&PID_[0-9A-F]{4}', 'IgnoreCase'
    ).Value.ToUpperInvariant()
    $benchTokens = @(foreach ($benchKey in @(
        'DEVPKEY_Device_HardwareIds', 'DEVPKEY_Device_CompatibleIds'
    )) {
        foreach ($benchId in @($benchValues[$benchKey])) {
            foreach ($benchMatch in [regex]::Matches(
                [string]$benchId,
                '(?:VID_[0-9A-F]{4}&PID_[0-9A-F]{4}(?:&REV_[0-9A-F]{4})?|MI_[0-9A-F]{2}|(?:Dev)?Class_[0-9A-F]{2}&SubClass_[0-9A-F]{2}&Prot_?[0-9A-F]{2}|MS_COMP_MTP)',
                'IgnoreCase'
            )) {
                $benchMatch.Value.ToUpperInvariant()
            }
        }
    })
    [pscustomobject]@{
        UsbIdentity = $benchIdentity
        Class = $benchDevice.Class
        Status = $benchDevice.Status
        IdTokens = @($benchTokens | Sort-Object -Unique)
        Service = $benchValues['DEVPKEY_Device_Service']
        DriverProvider = $benchValues['DEVPKEY_Device_DriverProvider']
        DriverVersion = $benchValues['DEVPKEY_Device_DriverVersion']
        DriverInf = $benchValues['DEVPKEY_Device_DriverInfPath']
    }
})
[pscustomobject]@{
    ObservedAtUtc = [DateTimeOffset]::UtcNow.ToString('o')
    Observation = 'Present-only PnP snapshot; not an enumeration event timestamp'
    Devices = $benchRows
} | ConvertTo-Json -Depth 6
