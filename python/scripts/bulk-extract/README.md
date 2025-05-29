# 📦 bulk-extract

Utilidad DevOps para descomprimir masivamente archivos .zip y .7z de forma recursiva en cualquier directorio y sus subcarpetas.

---

## 🚀 Características

- Descomprime todos los archivos .zip y .7z encontrados recursivamente.
- Extrae cada archivo en una carpeta con su mismo nombre.
- Búsqueda automática en subcarpetas ilimitadas.
- Soporte para extensiones en mayúsculas y minúsculas.
- Manejo robusto de errores con reportes detallados.
- Principio KISS: simple, directo y confiable.

---

## 🧑‍💻 Requisitos

- Python 3.6 o superior
- Librería `py7zr` (para archivos .7z)

---

## ⚙️ Instalación

### Opción 1: Instalación directa

```bash
# Descargar el script
wget https://raw.githubusercontent.com/tu_usuario/bulk-extract/main/bulk-extract.py
# o
curl -O https://raw.githubusercontent.com/tu_usuario/bulk-extract/main/bulk-extract.py

# Hacer ejecutable
chmod +x bulk-extract.py

# Instalar dependencia para archivos 7z
pip install py7zr
```

### Opción 2: Con entorno virtual (recomendado)

```bash
# Crear entorno virtual
python -m venv .venv
```

Activar el entorno virtual:

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

Instalar dependencias:
```bash
pip install py7zr
```

## 🧾 Uso

```bash
python bulk-extract.py <ruta_directorio>
```

### Ejemplos de uso:

#### Ejemplo básico - directorio actual:
```bash
python bulk-extract.py .
```

#### Ejemplo con ruta relativa:
```bash
python bulk-extract.py ./backups
```

#### Ejemplo con ruta absoluta:
```bash
python bulk-extract.py /var/backups/compressed
```

#### Ejemplo para deployment artifacts:
```bash
python bulk-extract.py ~/deployments/artifacts
```

---

## 📁 Comportamiento de extracción

El script funciona de la siguiente manera:

```
📂 proyecto/
 ├── 📦 app-v1.0.zip        → se extrae a: 📂 app-v1.0/
 ├── 📂 backups/
 │    ├── 📦 db-backup.7z   → se extrae a: 📂 db-backup/
 │    └── 📦 logs.ZIP       → se extrae a: 📂 logs/
 └── 📂 releases/
      └── 📦 release.zip    → se extrae a: 📂 release/
```

**Características importantes:**
- Cada archivo se extrae en su **misma ubicación**
- La carpeta de extracción tiene el **mismo nombre** del archivo (sin extensión)
- Soporte para **.zip**, **.ZIP**, **.7z**, **.7Z**

---

## 📄 Ejemplo de salida

```bash
$ python bulk-extract.py ./deployment-files

Encontrados 3 archivos ZIP y 2 archivos 7z (búsqueda recursiva)
Directorio de trabajo: /home/user/deployment-files
------------------------------------------------------------
✓ Extraído: frontend-v2.1.zip
✓ Extraído: api/backend-service.zip
✗ Error al extraer corrupted-file.zip: Bad zipfile
✓ Extraído: database/backup-2024.7z
✓ Extraído: configs/settings.7Z
------------------------------------------------------------
Proceso completado: 4/5 archivos extraídos correctamente.
```

---

## 🛠️ Casos de uso DevOps

### 1. Deployment de artifacts:
```bash
# Extraer todos los deployables
python bulk-extract.py ./ci-artifacts
```

### 2. Procesamiento de backups:
```bash
# Descomprimir backups masivamente
python bulk-extract.py /var/backups/compressed
```

### 3. Análisis de logs comprimidos:
```bash
# Extraer logs para análisis
python bulk-extract.py ./log-archives
```

### 4. Release management:
```bash
# Preparar releases para distribución
python bulk-extract.py ./releases/pending
```

---

## 🔧 Integración con scripts

### Bash script ejemplo:
```bash
#!/bin/bash
# deploy-pipeline.sh

echo "Descargando artifacts..."
wget -r https://artifacts.company.com/latest/

echo "Extrayendo archivos comprimidos..."
python bulk-extract.py ./artifacts

echo "Deployment completado!"
```

### Como alias permanente:
```bash
# Agregar al .bashrc o .zshrc
alias bulkextract='python /path/to/bulk-extract.py'

# Uso:
bulkextract ~/downloads
```

---

## ⚠️ Consideraciones importantes

- **Espacio en disco**: Asegúrate de tener suficiente espacio antes de extraer
- **Permisos**: El script necesita permisos de escritura en el directorio
- **Archivos existentes**: Las carpetas de extracción se sobreescriben si ya existen
- **Sin py7zr**: Los archivos .7z se omiten si la librería no está instalada

---

## 🐛 Solución de problemas

### Error: "py7zr no está instalado"
```bash
pip install py7zr
```

### Error: "Permission denied"
```bash
# Verificar permisos del directorio
ls -la /path/to/directory

# Ejecutar con sudo si es necesario (no recomendado)
sudo python bulk-extract.py /restricted/path
```

### Archivos corruptos:
- El script continúa con los siguientes archivos
- Revisa los archivos marcados con ✗ en la salida

---

## 📈 Tips de productividad

1. **Crear script wrapper personalizado**:
```bash
#!/bin/bash
# my-extract.sh
cd ~/work-directory
python ~/tools/bulk-extract.py "$1"
cd -
```

2. **Usar con find para casos específicos**:
```bash
# Extraer solo archivos modificados hoy
find . -name "*.zip" -mtime -1 -exec dirname {} \; | sort -u | xargs -I {} python bulk-extract.py {}
```

3. **Integrar en Makefile**:
```makefile
extract-artifacts:
	python bulk-extract.py ./build/artifacts
	
deploy: extract-artifacts
	# resto del deployment
```