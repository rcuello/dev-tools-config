# 🔍 graylog-checker

Verifica la conectividad completa con servidores Graylog, probando interfaces web, OpenSearch, y enviando mensajes de prueba via Syslog y GELF UDP.

---

## 🚀 Características

- Verifica múltiples componentes de Graylog en una sola ejecución.
- Configuración flexible mediante archivos YAML.
- Generación de reportes detallados de conectividad.
- Soporte para servidores remotos y configuraciones personalizadas.
- Modo verbose para debugging avanzado.
- Timeouts configurables para entornos lentos.

---

## 🧑‍💻 Requisitos

- Python 3.9 o superior
- Librerías: `requests`, `pyyaml`

---

## ⚙️ Instalación

Clona el repositorio y configura el entorno virtual:

```bash
git clone https://github.com/tu_usuario/graylog-checker.git
cd graylog-checker
python -m venv .venv
```

Activa el entorno virtual:

* En Linux/macOS:

```bash
source .venv/bin/activate
```

* En Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

* En Windows (cmd.exe):

```cmd
.\.venv\Scripts\activate.bat
```

Luego instala las dependencias con pip:

```bash
pip install -r requirements.txt
```

---

## 🧾 Uso

### Uso básico (localhost):

```bash
python graylog_checker.py
```

### Verificar servidor remoto:

```bash
python graylog_checker.py --host graylog.miempresa.com
```

### Con configuración personalizada:

```bash
python graylog_checker.py --config mi_graylog.yml --verbose
```

### Generar reporte detallado:

```bash
python graylog_checker.py --host 192.168.1.100 --output reporte.txt --verbose
```

---

## 🧱 Estructura del archivo de configuración `graylog.yml`

```yaml
# Configuración del servidor
host: "graylog.miempresa.com"
timeout: 10

# Puertos de servicios
ports:
  web: 9001
  syslog_udp: 1514
  gelf_udp: 12201
  opensearch: 9200

# Mensajes de prueba personalizados
test_messages:
  syslog:
    facility: "mi-servidor-app"
    message: "Mensaje de prueba Syslog personalizado"
  gelf:
    host: "ecommerce-backend"
    short_message: "Test order processed"
    full_message: "Order #TEST-001 processed successfully for testing connectivity"
```

---

## 📊 Argumentos disponibles

| Argumento | Descripción | Ejemplo |
|-----------|-------------|---------|
| `--host` | Host del servidor Graylog | `--host graylog.empresa.com` |
| `--config` | Archivo YAML de configuración | `--config produccion.yml` |
| `--timeout` | Timeout en segundos | `--timeout 15` |
| `--verbose` | Información detallada | `--verbose` |
| `--output` | Archivo de reporte | `--output conectividad.txt` |
| `--help` | Ayuda del comando | `--help` |

---

## 📄 Ejemplo de salida

### ✅ Conectividad exitosa:

```
🔍 Probando Graylog en localhost...
────────────────────────────────────────
✅ Web Interface: OK (Status: 200)
✅ OpenSearch: OK (Status: green)
✅ Syslog UDP: Mensaje enviado
✅ GELF UDP: Mensaje enviado
────────────────────────────────────────
🎉 TODAS LAS PRUEBAS PASARON (4/4)
✅ Graylog está funcionando correctamente
```

### ⚠️ Problemas de conectividad:

```
🔍 Probando Graylog en graylog-server...
────────────────────────────────────────
❌ Web Interface: FAILED
✅ OpenSearch: OK (Status: green)
✅ Syslog UDP: Mensaje enviado
❌ GELF UDP: FAILED
────────────────────────────────────────
⚠️  ALGUNAS PRUEBAS FALLARON (2/4)
❌ Revisar configuración de Graylog
```

---

## 🔧 Casos de uso comunes

### 1. Verificación rápida de desarrollo

```bash
# Verificar Graylog local
python graylog_checker.py
```

### 2. Monitoreo de producción

```bash
# Configuración específica para producción
python graylog_checker.py --config produccion.yml --output /var/log/graylog-health.txt
```

### 3. Debugging detallado

```bash
# Información completa para troubleshooting
python graylog_checker.py --host problema-server --verbose --timeout 30
```

### 4. Verificación automatizada

```bash
# Para scripts de CI/CD
python graylog_checker.py --host $GRAYLOG_HOST --config $CONFIG_FILE
echo $? # Código de salida: 0=éxito, 1=fallo
```

---

## 📈 Integración con monitoreo

### Script de Nagios/Icinga:

```bash
#!/bin/bash
RESULT=$(python graylog_checker.py --host $1 2>/dev/null)
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "OK - Graylog services are healthy"
    exit 0
else
    echo "CRITICAL - Graylog connectivity issues detected"
    exit 2
fi
```

### Cron job para monitoreo continuo:

```bash
# Verificar cada 5 minutos
*/5 * * * * /path/to/graylog_checker.py --config /etc/graylog-monitor.yml --output /var/log/graylog-check.log
```

---

## 🐛 Troubleshooting

### Problema: Connection refused en web interface

**Solución:**
- Verificar que Graylog esté ejecutándose
- Confirmar el puerto correcto (default: 9001)
- Revisar firewall y configuración de red

### Problema: OpenSearch no responde

**Solución:**
- Verificar que OpenSearch/Elasticsearch esté activo
- Confirmar puerto (default: 9200)
- Revisar logs de OpenSearch

### Problema: Mensajes UDP no se envían

**Solución:**
- Verificar puertos UDP (1514 para Syslog, 12201 para GELF)
- Confirmar que no hay firewall bloqueando UDP
- Revisar inputs configurados en Graylog

---

## 📝 requirements.txt

```
requests>=2.28.0
PyYAML>=6.0
```

---


## 🔗 Enlaces útiles

- [Documentación oficial de Graylog](https://go2docs.graylog.org/current/home.htm)
- [GELF Format Specification](https://go2docs.graylog.org/current/getting_in_log_data/gelf.html)
- [Syslog RFC 3164](https://tools.ietf.org/html/rfc3164)