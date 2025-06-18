# Guía de Recuperación de Contraseñas de DBeaver

## Información General

A partir de DBeaver 6.1.3, las contraseñas de conexión a bases de datos se almacenan en forma cifrada en el disco. Esta guía te ayudará a recuperar esas contraseñas cuando sea necesario.

⚠️ **Importante**: Esta guía incluye comandos específicos para diferentes sistemas operativos. Asegúrate de usar el comando apropiado para tu plataforma.

## Paso 1: Identificar el Nombre Interno de la Conexión

### 1.1 Localizar la carpeta del workspace

Las rutas del workspace varían según el sistema operativo:

- **macOS**: `~/Library/DBeaverData/workspace6/General/.dbeaver`
- **Windows**: `%APPDATA%\DBeaverData\workspace6\General\.dbeaver`
- **Linux**: `~/.local/share/DBeaverData/workspace6/General/.dbeaver`


## Paso 2: Descifrar las Contraseñas Guardadas

### 2.1 Comandos por Sistema Operativo

Ejecuta el comando correspondiente a tu sistema operativo en una terminal:

#### macOS
```bash
openssl aes-128-cbc -d -K babb4a9f774ab853c96c2d653dfe544a -iv 00000000000000000000000000000000 -in "${HOME}/Library/DBeaverData/workspace6/General/.dbeaver/credentials-config.json" | dd bs=1 skip=16 2>/dev/null
```

#### Linux
```bash
openssl aes-128-cbc -d -K babb4a9f774ab853c96c2d653dfe544a -iv 00000000000000000000000000000000 -in "${HOME}/.local/share/DBeaverData/workspace6/General/.dbeaver/credentials-config.json" | dd bs=1 skip=16 2>/dev/null
```

#### Windows (PowerShell)
```powershell
# Nota: Requiere OpenSSL instalado en Windows
openssl aes-128-cbc -d -K babb4a9f774ab853c96c2d653dfe544a -iv 00000000000000000000000000000000 -in "$env:APPDATA\DBeaverData\workspace6\General\.dbeaver\credentials-config.json" | dd bs=1 skip=16 2>$null
```

### 2.2 Interpretar los Resultados

El comando mostrará todas las contraseñas de conexión en formato JSON. Busca la entrada que corresponda al nombre interno de conexión que identificaste en el Paso 1.

**Ejemplo de salida**:
```json
{
  "postgres-jdbc-518abbb622c440–2622869e2d1e85b5dd9": {
    "#connection": {
            "user": "postgres",
            "password": "postgres"
    }
  }
}
```

## Consideraciones de Seguridad

🔒 **Importantes medidas de seguridad**:

1. **Acceso físico**: Este método requiere acceso físico o remoto al sistema donde está instalado DBeaver
2. **Permisos**: Asegúrate de tener los permisos necesarios para acceder a los archivos de configuración
3. **Uso responsable**: Utiliza esta información únicamente para conexiones propias o con autorización explícita
4. **Limpieza**: Considera limpiar el historial de comandos después de ejecutar estos comandos:
   ```bash
   history -c  # Bash
   Clear-History  # PowerShell
   ```

## Casos de Uso Comunes

- **Migración de entorno**: Recuperar contraseñas para configurar DBeaver en una nueva máquina
- **Documentación**: Actualizar documentación de conexiones a bases de datos
- **Auditoría**: Verificar qué conexiones están configuradas y sus credenciales
- **Troubleshooting**: Diagnosticar problemas de conectividad

## Troubleshooting

### Problemas Comunes

1. **Archivo no encontrado**: Verifica que la ruta del workspace sea correcta para tu sistema operativo
2. **OpenSSL no disponible**: Instala OpenSSL en tu sistema:
   - macOS: `brew install openssl`
   - Linux: `apt-get install openssl` o `yum install openssl`
   - Windows: Descarga desde https://slproweb.com/products/Win32OpenSSL.html

3. **Permisos denegados**: Asegúrate de tener permisos de lectura en la carpeta del workspace

### Versiones de DBeaver

Esta guía es válida para DBeaver 6.1.3 en adelante. Para versiones anteriores, las contraseñas podrían estar almacenadas en texto plano.

## Referencias

- Método basado en: https://stackoverflow.com/a/64726416
- Documentación oficial de DBeaver: https://dbeaver.io/
- Información de seguridad de DBeaver: https://github.com/dbeaver/dbeaver/wiki/Security

