@echo off
setlocal enabledelayedexpansion

:: Configuración de depuración
set DEBUG="true"  :: Cambia a "false" para desactivar los mensajes detallados

:: Llamar a la función para buscar jar.exe
call :find_jar_path

:: Verificar si se encontró jar.exe
if not defined FOUND_JAR_PATH (
    echo [ERROR] No se encontró jar.exe en ninguna ubicación.
    exit /b 1
)

:: Ejecutar jar.exe con los parámetros dados
echo ====================================
echo jar.exe encontrado en: "!FOUND_JAR_PATH!"
echo ====================================
"%FOUND_JAR_PATH%" %*
exit /b %ERRORLEVEL%


:: ====================================
:: Función para encontrar la ruta de jar.exe
:: ====================================
:find_jar_path
set FOUND_JAR_PATH=

:: Intentar encontrar Java en el PATH actual
where java >nul 2>nul
if %ERRORLEVEL% equ 0 (
    for /f "delims=" %%i in ('where java') do (
        set "JAVA_PATH=%%~dpni"
        set "JAVA_BIN_PATH=%JAVA_PATH%\.."

        :: Normalizar la ruta eliminando ".."
        for %%A in ("%JAVA_BIN_PATH%") do set "JAVA_BIN_PATH=%%~fA"

        if /i "%DEBUG%"=="true" echo [DEBUG] Java encontrado en: "%%i"
        if /i "%DEBUG%"=="true" echo [DEBUG] Normalizando ruta a: "!JAVA_BIN_PATH!"

        if exist "!JAVA_BIN_PATH!\jar.exe" (
            set "FOUND_JAR_PATH=!JAVA_BIN_PATH!\jar.exe"
            if /i "%DEBUG%"=="true" echo [DEBUG] jar.exe encontrado en: "!FOUND_JAR_PATH!"
            exit /b 0
        )
    )
)

:: Lista de ubicaciones comunes de instalación de Java
set "LOCATION[0]=C:\Program Files\Java"
set "LOCATION[1]=C:\Program Files (x86)\Java"
set "LOCATION[2]=C:\Program Files\Eclipse Adoptium"
set "LOCATION[3]=C:\Program Files (x86)\Eclipse Adoptium"

:: Buscar en ubicaciones comunes
for /L %%i in (0,1,3) do (
    set "CURRENT_LOCATION=!LOCATION[%%i]!"
    
    if exist "!CURRENT_LOCATION!" (
        if /i "%DEBUG%"=="true" echo [DEBUG] Verificando directorio: "!CURRENT_LOCATION!"

        for /d %%j in ("!CURRENT_LOCATION!\*") do (
            if exist "%%~j\bin\jar.exe" (
                set "FOUND_JAR_PATH=%%~j\bin\jar.exe"
                if /i "%DEBUG%"=="true" echo [DEBUG] jar.exe encontrado en: "!FOUND_JAR_PATH!"
                exit /b 0
            )
        )
    )
)

:: Buscar dinámicamente en "C:\Program Files\Java\jdk-*"
if exist "C:\Program Files\Java\" (
    if /i "%DEBUG%"=="true" echo [DEBUG] Buscando dinámicamente en "C:\Program Files\Java\jdk-*"

    for /d %%j in ("C:\Program Files\Java\jdk-*") do (
        if exist "%%~j\bin\jar.exe" (
            set "FOUND_JAR_PATH=%%~j\bin\jar.exe"
            if /i "%DEBUG%"=="true" echo [DEBUG] jar.exe encontrado en: "!FOUND_JAR_PATH!"
            exit /b 0
        )
    )
)

exit /b 1
