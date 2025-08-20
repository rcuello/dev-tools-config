# 📄 md-to-pdf

Convierte archivos Markdown (`.md`) a PDF usando **Playwright**. Soporta emojis a color, estilos CSS personalizados y configuración flexible de márgenes y tamaño de página.

---

## 🚀 Características

- Conversión de Markdown a PDF con tipografía moderna
- Soporte nativo para **emojis a color**
- Estilos CSS personalizables
- Control de tamaño de página y márgenes
- Generación opcional de tabla de contenidos
- Compatible con Linux, macOS y Windows

---

## 🧑‍💻 Requisitos

- Python 3.9+
- [Playwright](https://playwright.dev/python/) y navegadores instalados

Instalación de dependencias:

```bash
pip install -r requirements.txt
playwright install
````

O con hosts de confianza:

```bash
pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
playwright install
```

Contenido mínimo del `requirements.txt`:

```txt
markdown==3.5.2
playwright==1.44.0
```

---

## ⚙️ Instalación

```bash
git clone https://github.com/tu_usuario/md-to-pdf.git
cd md-to-pdf
python -m venv .venv
source .venv/bin/activate  # o en Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org

playwright install
```

---

## 🧾 Uso

### Conversión básica:

```bash
python md_to_pdf.py documento.md
```

### Especificar archivo de salida:

```bash
python md_to_pdf.py documento.md -o salida.pdf
```

### Aplicar estilos CSS personalizados:

```bash
python md_to_pdf.py documento.md --css-file estilos.css
```

### Definir tamaño de página y márgenes:

```bash
python md_to_pdf.py documento.md --page-size Letter --margins "25,20,25,20"
```

### Desactivar tabla de contenidos:

```bash
python md_to_pdf.py documento.md --no-toc
```

### Ejecutar en modo silencioso (sin mensajes):

```bash
python md_to_pdf.py documento.md --quiet
```

---

## 🖋️ Estilos personalizados

Puedes usar un archivo `estilos.css` para personalizar la salida PDF. Ejemplo:

```css
body {
    font-family: 'Noto Sans', sans-serif;
    font-size: 12pt;
    line-height: 1.6;
}

h1 {
    color: #2c3e50;
    font-size: 24pt;
    border-bottom: 2px solid #3498db;
}

code {
    background-color: #f0f0f0;
    padding: 2px 4px;
    border-radius: 4px;
}
```

---

## 📐 Tamaños de página soportados

* `A4` (predeterminado)
* `A3`
* `A5`
* `Letter`
* `Legal`

### Márgenes

Se definen en milímetros como: `"top,right,bottom,left"`, por ejemplo:

```bash
--margins "20,15,20,15"
```

---

## 📖 Argumentos disponibles

| Argumento      | Descripción                                   | Valor por defecto       |
| -------------- | --------------------------------------------- | ----------------------- |
| `input_file`   | Archivo Markdown de entrada                   | Obligatorio             |
| `-o, --output` | Archivo PDF de salida                         | `<nombre>.pdf`          |
| `--css-file`   | Ruta a archivo CSS para personalización       | Estilos predeterminados |
| `--page-size`  | Tamaño de página (`A4`, `Letter`, etc.)       | `A4`                    |
| `--margins`    | Márgenes en `"top,right,bottom,left"` (en mm) | `"20,20,20,20"`         |
| `--no-toc`     | Desactiva la tabla de contenidos              | `False`                 |
| `--quiet`      | Oculta mensajes en consola                    | `False`                 |

---

## ✅ Características Markdown soportadas

* ✅ Títulos (H1-H6)
* ✅ Texto en **negrita**, *cursiva* y ~~tachado~~
* ✅ Listas (ordenadas y sin orden)
* ✅ Enlaces e imágenes
* ✅ Código y bloques de código
* ✅ Citas (`blockquote`)
* ✅ Tablas
* ✅ Líneas horizontales
* ✅ Tabla de contenidos opcional
* ✅ Soporte para [Markdown Extra](https://python-markdown.github.io/extensions/)

---

## 💡 Notas técnicas

* El motor de renderizado es **Chromium** vía Playwright.
* Se priorizan fuentes compatibles con emojis a color:

  * `'Segoe UI Emoji'`, `'Noto Color Emoji'`, `'Apple Color Emoji'`, etc.
* No se requiere instalación de WeasyPrint ni motores adicionales.
* Puedes ajustar márgenes y tamaños como en un diseño profesional.

---

## 🛠️ Solución de problemas

### Playwright no instalado

```bash
pip install playwright
playwright install
```

### Error de codificación del archivo Markdown

```bash
# Asegúrate de que tu archivo está en UTF-8
# o abrelo con encoding correcto antes de convertirlo
```

---

## 📂 Ejemplos

```bash
# Básico
python md_to_pdf.py ejemplo.md

# PDF con márgenes amplios y sin TOC
python md_to_pdf.py ejemplo.md --margins "30,30,30,30" --no-toc

# Con estilo propio y salida personalizada
python md_to_pdf.py ejemplo.md -o informe.pdf --css-file mi_estilo.css
```


---