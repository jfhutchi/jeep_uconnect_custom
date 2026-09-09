param(
    [string]$JdkHome = $env:JAVA_HOME,
    [string]$Python = $env:HELLO_UCONNECT_PYTHON
)

$ErrorActionPreference = 'Stop'
$root = [System.IO.Path]::GetFullPath($PSScriptRoot)
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $root '..\..'))
$buildRoot = [System.IO.Path]::GetFullPath((Join-Path $root 'build'))
if (-not $buildRoot.StartsWith($root + [System.IO.Path]::DirectorySeparatorChar)) {
    throw 'Refusing to use a build directory outside the Hello Uconnect project.'
}

if ([string]::IsNullOrWhiteSpace($JdkHome)) {
    $javacCommand = Get-Command javac -ErrorAction SilentlyContinue
    if ($null -eq $javacCommand) {
        throw 'JDK 8 javac is required. Pass -JdkHome or set JAVA_HOME.'
    }
    $javac = $javacCommand.Source
} else {
    $javac = Join-Path $JdkHome 'bin\javac.exe'
    if (-not (Test-Path -LiteralPath $javac)) {
        $javac = Join-Path $JdkHome 'bin\javac'
    }
}
if (-not (Test-Path -LiteralPath $javac)) {
    throw "javac was not found at $javac"
}
$toolchain = Get-Content -Raw -LiteralPath (Join-Path $root 'toolchain.json') |
    ConvertFrom-Json
$javacVersion = ((& $javac -version 2>&1) -join '').Trim()
if ($LASTEXITCODE -ne 0) {
    throw "javac version check failed with exit code $LASTEXITCODE"
}
if ($javacVersion -ne $toolchain.javac_version) {
    throw "Unpinned compiler '$javacVersion'; expected '$($toolchain.javac_version)'."
}

if ([string]::IsNullOrWhiteSpace($Python)) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $pythonCommand) {
        throw 'Python 3 is required. Pass -Python or set HELLO_UCONNECT_PYTHON.'
    }
    $Python = $pythonCommand.Source
}
if (-not (Test-Path -LiteralPath $Python)) {
    throw "Python was not found at $Python"
}

if (Test-Path -LiteralPath $buildRoot) {
    Remove-Item -LiteralPath $buildRoot -Recurse -Force
}
$compileApiClasses = Join-Path $buildRoot 'work\compile-api-classes'
$applicationClasses = Join-Path $buildRoot 'work\application-classes'
$output = Join-Path $buildRoot 'out'
New-Item -ItemType Directory -Path $compileApiClasses, $applicationClasses, $output | Out-Null

$compileApiSources = @(
    Get-ChildItem -LiteralPath (Join-Path $root 'compile_api\src') -Recurse -Filter '*.java' |
        Sort-Object FullName |
        ForEach-Object FullName
)
$applicationSources = @(
    Get-ChildItem -LiteralPath (Join-Path $root 'src') -Recurse -Filter '*.java' |
        Sort-Object FullName |
        ForEach-Object FullName
)
if ($compileApiSources.Count -eq 0 -or $applicationSources.Count -eq 0) {
    throw 'Compile API or application Java sources are missing.'
}

& $javac -source 1.4 -target 1.4 -encoding US-ASCII -d $compileApiClasses $compileApiSources
if ($LASTEXITCODE -ne 0) {
    throw "Compile API javac failed with exit code $LASTEXITCODE"
}
& $javac -source 1.4 -target 1.4 -encoding US-ASCII -classpath $compileApiClasses -d $applicationClasses $applicationSources
if ($LASTEXITCODE -ne 0) {
    throw "Application javac failed with exit code $LASTEXITCODE"
}

$jarPath = Join-Path $output 'hello-uconnect.jar'
Push-Location $repoRoot
try {
    & $Python -m prototype.hello_uconnect.tools.build_artifact $applicationClasses $jarPath | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Deterministic JAR build failed with exit code $LASTEXITCODE"
    }
    Copy-Item -LiteralPath (Join-Path $root 'descriptor\xlet.properties') -Destination $output
    Copy-Item -LiteralPath (Join-Path $root 'README.md') -Destination (Join-Path $output 'BUILD-INSTRUCTIONS.md')
    Copy-Item -LiteralPath (Join-Path $root 'toolchain.json') -Destination $output
    & $Python -m prototype.hello_uconnect.tools.validate_artifact `
        $jarPath `
        (Join-Path $output 'xlet.properties') `
        (Join-Path $root 'api-allowlist.json') `
        $output
    if ($LASTEXITCODE -ne 0) {
        throw "Artifact validation failed with exit code $LASTEXITCODE"
    }
    $researchLayout = Join-Path $buildRoot 'research-installed-layout'
    & $Python -m prototype.hello_uconnect.tools.build_installed_layout_skeleton `
        $jarPath `
        (Join-Path $output 'xlet.properties') `
        $researchLayout | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Installed-layout skeleton build failed with exit code $LASTEXITCODE"
    }
    $researchApp = Join-Path $researchLayout '4e9838d7-d08f-5f3a-be95-b309114fc22e'
    & $Python -m analysis_tools.resident_package_inspect `
        $researchApp `
        --hello-profile `
        --pretty `
        --output (Join-Path $output 'installed-layout-research-report.json')
    if ($LASTEXITCODE -ne 1) {
        throw "Unsigned skeleton must fail installability inspection with exit code 1; got $LASTEXITCODE"
    }
    # Exit 1 is the expected non-installability result, not a host-build failure.
    $global:LASTEXITCODE = 0
} finally {
    Pop-Location
}
