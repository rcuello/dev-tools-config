# Descripción: Encuentra la ruta del JDK y agrega jar.exe al PATH en Windows.
# Autor: Ronald Cuello

function Find-JavaHome {
    # Intentar múltiples métodos para encontrar la ruta del JDK
    
    # Método 1: Variable de entorno JAVA_HOME
    if ($env:JAVA_HOME) {
        $javaHome = $env:JAVA_HOME
        Write-Verbose "JDK encontrado mediante variable JAVA_HOME: $javaHome"
        return $javaHome
    }

    # Método 2: Buscar en rutas de instalación comunes de Java
    $possiblePaths = @(
        "C:\Program Files\Java\*",
        "C:\Program Files (x86)\Java\*",
        "C:\Program Files\Eclipse Adoptium\*",
        "C:\Program Files (x86)\Eclipse Adoptium\*"
    )

    foreach ($path in $possiblePaths) {
        $jdkFolder = Get-ChildItem -Path $path -Directory | 
            Where-Object { $_.Name -match 'jdk|jre' } | 
            Sort-Object Name -Descending | 
            Select-Object -First 1

        if ($jdkFolder) {
            Write-Verbose "JDK encontrado en ruta común: $($jdkFolder.FullName)"
            return $jdkFolder.FullName
        }
    }

    # Método 3: Usar el comando 'java' para encontrar la ruta
    try {
        $javaExePath = (Get-Command java -ErrorAction Stop).Source
        $javaHome = Split-Path -Path (Split-Path -Path $javaExePath) -Parent
        Write-Verbose "JDK encontrado mediante comando java: $javaHome"
        return $javaHome
    }
    catch {
        Write-Error "No se pudo encontrar la instalación de Java/JDK"
        return $null
    }
}

function Set-JarPath {
    param(
        [Parameter(Mandatory=$true)]
        [string]$JdkPath
    )

    # Construir rutas específicas
    $binPath = Join-Path -Path $JdkPath -ChildPath "bin"
    $jarPath = Join-Path -Path $binPath -ChildPath "jar.exe"

    # Verificar existencia de jar.exe
    if (-not (Test-Path $jarPath)) {
        Write-Error "jar.exe no encontrado en $jarPath"
        return $false
    }

    try {
        # Obtener PATH actual del usuario
        $currentPath = $env:Path

        # Verificar si la ruta ya está en PATH
        if ($currentPath -split ';' -contains $binPath) {
            Write-Host "La ruta $binPath ya está configurada en PATH" -ForegroundColor Green
            return $true
        }

        # Agregar nueva ruta al PATH del usuario actual
        $env:Path = $binPath + ";" + $currentPath

        # Guardar el cambio de PATH para la sesión actual del usuario
        [Environment]::SetEnvironmentVariable("Path", $env:Path, "User")

        Write-Host "Configuración completada:" -ForegroundColor Green
        Write-Host "- Ruta JDK: $JdkPath" -ForegroundColor Cyan
        Write-Host "- Ruta bin agregada al PATH: $binPath" -ForegroundColor Cyan
        Write-Host "NOTA: Los cambios se aplicarán en nuevas terminales" -ForegroundColor Yellow

        return $true
    }
    catch {
        Write-Error "Error al configurar PATH: $_"
        return $false
    }
}

# Ejecución principal del script
function Main {
    # Habilitar verbose para más detalles
    $VerbosePreference = 'Continue'

    # Buscar la ruta del JDK
    $jdkPath = Find-JavaHome

    if (-not $jdkPath) {
        Write-Error "No se encontró una instalación de JDK"
        exit 1
    }

    # Configurar JAR en PATH
    $result = Set-JarPath -JdkPath $jdkPath

    if ($result) {
        Write-Host "Proceso completado exitosamente" -ForegroundColor Green
    }
    else {
        Write-Error "Falló la configuración de JAR en PATH"
    }
}

# Ejecutar el script principal
Main