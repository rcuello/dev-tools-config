# 📂 scan-directory

Genera un árbol de directorios en formato visual, con soporte para exclusiones configurables mediante un archivo YAML.

---

## 🚀 Características

- Genera un esquema en árbol de cualquier directorio local.
- Permite excluir carpetas y archivos mediante un archivo `ignore.yml`.
- Compatible con entornos virtuales.
- Fácil de usar y configurar.

---

## 🧑‍💻 Requisitos

- Python 3.9 o superior
- [Poetry](https://python-poetry.org/) (para gestión de dependencias)

---

## ⚙️ Instalación

Clona el repositorio y configura el entorno:

```bash
git clone https://github.com/tu_usuario/scan-directory.git
cd scan-directory
poetry install
````

Activa el entorno virtual:

```bash
poetry shell
```

---

## 🧾 Uso

```bash
python scan_directory.py <ruta_directorio> [--ignore-file ignore.yml]
```

### Ejemplo básico:

```bash
python scan_directory.py ./mi_proyecto
```

### Ejemplo con exclusiones:

```bash
python scan_directory.py ./mi_proyecto --ignore-file ignore.yml
```

---

## 🧱 Estructura del archivo `ignore.yml`

```yaml
ignore_directories:
  - __pycache__
  - .git
  - .venv

ignore_files:
  - "*.pyc"
  - "*.log"
```

---

## 📄 Ejemplo de salida

```
📂 mi_proyecto
 ├── 📂 app
 │    ├── main.py
 │    └── utils.py
 ├── 📂 data
 │    └── input.csv
 └── README.md
```
