# DevToolsConfig

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Una colección de scripts y herramientas para automatizar la configuración de entornos de desarrollo. Diseñado para ahorrar tiempo y garantizar configuraciones consistentes en diferentes equipos.

## 🚀 Propósito

Este repositorio aloja scripts "helper" que automatizan tareas comunes de configuración para desarrolladores:

- Configuración de variables de entorno
- Instalación y configuración de herramientas de desarrollo
- Solución rápida de problemas comunes de configuración
- Estandarización de entornos de desarrollo

## 📋 Contenido

### PowerShell Scripts

| Script | Descripción | Uso |
|--------|-------------|-----|
| [configurar-jar-en-path.ps1](powershell/java/configurar-jar-en-path.ps1) | Detecta automáticamente la instalación de JDK y configura jar.exe en el PATH | `.\configurar-jar-en-path.ps1` |
| [otro-script.ps1](powershell/otro-script.ps1) | Descripción del script | `.\otro-script.ps1` |

### Bash Scripts

*Próximamente*

## 🔧 Uso

La mayoría de los scripts están diseñados para ser ejecutados directamente sin necesidad de parámetros adicionales. Consulta la documentación específica de cada script para obtener más detalles.

```powershell
# Ejemplo de uso básico
.\powershell\configurar-jar-en-path.ps1
```

## 🔍 Solución de problemas (Troubleshooting)

En esta sección se documenta la solución a problemas comunes durante la configuración de entornos de desarrollo:

### Problemas con Java/JDK

**Problema**: jar.exe no se encuentra en el PATH  
**Solución**: Ejecuta [configurar-jar-en-path.ps1](powershell/configurar-jar-en-path.ps1)

```powershell
.\powershell\configurar-jar-en-path.ps1
```

**Problema**: Otro problema relacionado con Java  
**Solución**: Descripción de la solución o referencia al script que lo resuelve

### Problemas con WSL 
**Problema**: Olvidaste la contraseña del usuario en WSL (Ubuntu).
**Solución**: Sigue los pasos detallados en la guía: [Restablecer contraseña en WSL](docs/problemas-comunes/reset-wsl-password.md).

### Problemas con otras herramientas

*Próximamente*

## 📦 Requisitos

- PowerShell 5.1 o superior para scripts .ps1
- Permisos de usuario para modificar variables de entorno
- Se recomienda ejecución como administrador para algunas funcionalidades

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Si deseas agregar un nuevo script o mejorar los existentes:

1. Haz un fork del proyecto
2. Crea una rama para tu característica (`git checkout -b feature/amazing-script`)
3. Haz commit de tus cambios (`git commit -m 'Agrega un nuevo script para configurar X'`)
4. Haz push a la rama (`git push origin feature/amazing-script`)
5. Abre un Pull Request

### Directrices para contribuciones

- Todos los scripts deben incluir comentarios descriptivos
- Agrega manejo de errores adecuado
- Incluye ejemplos de uso en la documentación del script
- Actualiza el README.md con información sobre tu script

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.

## ✨ Autor

**Ronald Cuello**