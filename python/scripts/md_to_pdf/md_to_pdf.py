#!/usr/bin/env python3
"""
Markdown to PDF Converter con soporte para Mermaid
===================================================

Script que convierte archivos Markdown (.md) a formato PDF
usando Playwright con soporte mejorado para imágenes y diagramas Mermaid.

Uso:
----
  python md_to_pdf.py [OPCIONES] ARCHIVO_DE_ENTRADA

Ejemplo:
--------
    python md_to_pdf.py documento.md

Dependencias requeridas:
------------------------
- markdown
- playwright
- aiohttp
- Para instalar navegadores: `playwright install`
"""

import sys
import argparse
import markdown
import asyncio
import base64
import mimetypes
import re
import json
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse
from playwright.async_api import async_playwright
import aiohttp

# TODO: Hacer archivo externo .css y html
# DEFAULT_CSS_FILE = Path(__file__).with_name("default.css")

# CSS optimizado con soporte para Mermaid
# Ruta CSS por defecto

DEFAULT_CSS = """
@page {
    margin: 2cm;
    size: A4;
}

body {
    font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 
                 'Symbola', 'DejaVu Sans', Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    font-size: 12pt;
}

h1, h2, h3, h4, h5, h6 {
    color: #2c3e50;
    margin-top: 1.5em;
    margin-bottom: 0.8em;
    font-weight: bold;
}

h1 {
    border-bottom: 2px solid #3498db;
    padding-bottom: 0.3em;
}

h2 {
    border-bottom: 1px solid #bdc3c7;
    padding-bottom: 0.2em;
}

code {
    background-color: #f8f9fa;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: 'Consolas', 'DejaVu Sans Mono', monospace;
    font-size: 0.9em;
}

pre {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 4px;
    padding: 1em;
    overflow-x: auto;
}

blockquote {
    border-left: 4px solid #3498db;
    margin: 1em 0;
    padding: 0.5em 1em;
    background-color: #f8f9fa;
    font-style: italic;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}

th {
    background-color: #f2f2f2;
    font-weight: bold;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1em auto;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

p {
    margin: 0.8em 0;
}

ul, ol {
    margin: 0.8em 0;
    padding-left: 1.5em;
}

/* Estilos para diagramas Mermaid */
.mermaid-container {
    margin: 1.5em 0;
    text-align: center;
    background-color: #fff;
    border: 1px solid #e1e8ed;
    border-radius: 6px;
    padding: 1em;
}

.mermaid-error {
    background-color: #f8d7da;
    color: #721c24;
    padding: 0.75rem 1.25rem;
    margin: 1rem 0;
    border: 1px solid #f5c6cb;
    border-radius: 0.25rem;
}

.image-error {
    background-color: #f8d7da;
    color: #721c24;
    padding: 0.75rem 1.25rem;
    margin: 1rem 0;
    border: 1px solid #f5c6cb;
    border-radius: 0.25rem;
}

/* Mejoras para imágenes */
img[src^="data:"] {
    max-height: 600px;
}
"""

# HTML template que incluye Mermaid
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{css_content}</style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.6.1/mermaid.min.js"></script>
</head>
<body>
{html_body}

<script>
mermaid.initialize({{
    startOnLoad: true,
    theme: 'default',
    securityLevel: 'loose',
    flowchart: {{
        useMaxWidth: true,
        htmlLabels: true
    }},
    sequence: {{
        diagramMarginX: 50,
        diagramMarginY: 10,
        actorMargin: 50,
        width: 150,
        height: 65,
        boxMargin: 10,
        boxTextMargin: 5,
        noteMargin: 10,
        messageMargin: 35
    }}
}});

// Función para renderizar diagramas después de cargar la página
window.addEventListener('load', function() {{
    setTimeout(() => {{
        mermaid.init(undefined, '.language-mermaid');
    }}, 100);
}});
</script>
</body>
</html>"""


class MarkdownToPDFConverter:
    """Conversor mejorado de Markdown a PDF con soporte para Mermaid."""
    
    def __init__(self, quiet: bool = False):
        self.quiet = quiet
    
    def _log(self, message: str) -> None:
        """Imprime mensajes informativos si no está en modo silencioso."""
        if not self.quiet:
            print(message)
    
    def _load_file(self, file_path: Path) -> str:
        """Carga el contenido de un archivo."""
        try:
            return file_path.read_text(encoding='utf-8')
        except FileNotFoundError:
            raise FileNotFoundError(f"Archivo no encontrado: '{file_path}'")
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(f"Error de codificación en '{file_path}': {e}")
    
    def _get_image_as_base64(self, image_path: Path) -> Tuple[str, str]:
        """Convierte una imagen local a base64 data URL."""
        try:
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
                mime_type = mimetypes.guess_type(str(image_path))[0] or 'image/png'
                base64_data = base64.b64encode(img_data).decode('utf-8')
                return f"data:{mime_type};base64,{base64_data}", ""
        except Exception as e:
            self._log(f"⚠️  Error al procesar imagen {image_path}: {e}")
            return "", str(e)
    
    async def _get_remote_image_as_base64(self, url: str) -> Tuple[str, str]:
        """Descarga una imagen remota y la convierte a base64 data URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        img_data = await response.read()
                        content_type = response.headers.get('content-type', 'image/png')
                        base64_data = base64.b64encode(img_data).decode('utf-8')
                        return f"data:{content_type};base64,{base64_data}", ""
                    else:
                        return "", f"HTTP {response.status}"
        except Exception as e:
            self._log(f"⚠️  Error al descargar imagen {url}: {e}")
            return "", str(e)
    
    def _is_url(self, path: str) -> bool:
        """Verifica si una ruta es una URL."""
        parsed = urlparse(path)
        return parsed.scheme in ('http', 'https')
    
    async def _process_images_in_html(self, html_content: str, base_path: Path) -> str:
        """Procesa todas las imágenes en el HTML y las convierte a base64."""
        img_pattern = re.compile(r'<img[^>]*src=["\']([^"\']*)["\'][^>]*>', re.IGNORECASE)
        
        async def replace_img_src(match):
            img_tag = match.group(0)
            img_src = match.group(1)
            
            if img_src.startswith('data:'):
                return img_tag
            
            data_url, error_msg = "", ""
            
            if self._is_url(img_src):
                self._log(f"📥 Descargando imagen remota: {img_src}")
                data_url, error_msg = await self._get_remote_image_as_base64(img_src)
            else:
                img_path = base_path.parent / img_src if not Path(img_src).is_absolute() else Path(img_src)
                
                if img_path.exists():
                    self._log(f"📁 Procesando imagen local: {img_path}")
                    data_url, error_msg = self._get_image_as_base64(img_path)
                else:
                    error_msg = "Archivo no encontrado"
            
            if data_url:
                return img_tag.replace(f'src="{img_src}"', f'src="{data_url}"').replace(f"src='{img_src}'", f"src='{data_url}'")
            else:
                self._log(f"❌ No se pudo cargar imagen: {img_src} ({error_msg})")
                return f'<div class="image-error">⚠️ No se pudo cargar la imagen: {img_src}<br>Error: {error_msg}</div>'
        
        matches = list(img_pattern.finditer(html_content))
        if matches:
            self._log(f"🖼️  Procesando {len(matches)} imagen(es)...")
            
            result = html_content
            offset = 0
            for match in matches:
                start, end = match.span()
                replacement = await replace_img_src(match)
                result = result[:start + offset] + replacement + result[end + offset:]
                offset += len(replacement) - (end - start)
            
            return result
        
        return html_content
    
    def _process_mermaid_blocks(self, html_content: str) -> str:
        """Procesa bloques de código Mermaid y los convierte en divs renderizables."""
        # Patrón para detectar bloques de código mermaid
        mermaid_pattern = re.compile(
            r'<pre><code class="language-mermaid">(.*?)</code></pre>',
            re.DOTALL | re.IGNORECASE
        )
        
        def replace_mermaid(match):
            mermaid_code = match.group(1).strip()
            # Decodificar entidades HTML comunes
            mermaid_code = (mermaid_code
                           .replace('&lt;', '<')
                           .replace('&gt;', '>')
                           .replace('&amp;', '&')
                           .replace('&quot;', '"'))
            
            self._log(f"🎨 Procesando diagrama Mermaid")
            
            return f'''<div class="mermaid-container">
    <div class="language-mermaid">{mermaid_code}</div>
</div>'''
        
        result = mermaid_pattern.sub(replace_mermaid, html_content)
        
        # Contar cuántos diagramas se procesaron
        mermaid_count = len(mermaid_pattern.findall(html_content))
        if mermaid_count > 0:
            self._log(f"📊 Se encontraron {mermaid_count} diagrama(s) Mermaid")
        
        return result
    
    def _markdown_to_html(self, md_content: str, enable_toc: bool = True) -> str:
        """Convierte contenido Markdown a HTML."""
        extensions = ['extra', 'codehilite', 'tables', 'fenced_code']
        if enable_toc:
            extensions.append('toc')
        
        return markdown.markdown(md_content, extensions=extensions, output_format='html5')
    
    def _get_css_content(self, css_file: Optional[Path]) -> str:
        """Obtiene CSS personalizado o el predeterminado."""
        if css_file and css_file.is_file():
            custom_css = self._load_file(css_file)
            self._log(f"📄 Usando CSS personalizado: {css_file}")
            return custom_css
        
        #return DEFAULT_CSS_FILE.read_text(encoding="utf-8")
        return DEFAULT_CSS
    
    def _create_html_document(self, html_body: str, css_content: str, title: str) -> str:
        """Crea documento HTML completo con soporte para Mermaid."""
        return HTML_TEMPLATE.format(
            title=title,
            css_content=css_content,
            html_body=html_body
        )
    
    def _parse_margins(self, margins_str: str) -> dict:
        """Parsea márgenes en formato 'top,right,bottom,left'."""
        try:
            margins = [m.strip() for m in margins_str.split(',')]
            if len(margins) != 4:
                raise ValueError("Se requieren exactamente 4 valores")
            
            return {
                'top': f"{margins[0]}mm",
                'right': f"{margins[1]}mm",
                'bottom': f"{margins[2]}mm",
                'left': f"{margins[3]}mm"
            }
        except (ValueError, IndexError):
            raise ValueError("Formato de márgenes inválido. Use 'top,right,bottom,left' (en mm)")
    
    async def convert(self, input_file: Path, output_file: Optional[Path] = None,
                     css_file: Optional[Path] = None, page_size: str = 'A4',
                     margins: str = '20,20,20,20', no_toc: bool = False) -> Path:
        """Convierte un archivo Markdown a PDF."""
        if output_file is None:
            output_file = input_file.with_suffix('.pdf')
        
        self._log(f"🔄 Convirtiendo: '{input_file.name}' -> '{output_file.name}'")
        
        # Cargar y procesar contenido
        md_content = self._load_file(input_file)
        html_body = self._markdown_to_html(md_content, enable_toc=not no_toc)
        
        # Procesar diagramas Mermaid
        html_body = self._process_mermaid_blocks(html_body)
        
        # Procesar imágenes
        html_body = await self._process_images_in_html(html_body, input_file)
        
        css_content = self._get_css_content(css_file)
        full_html = self._create_html_document(html_body, css_content, input_file.stem)
        
        # Generar PDF con Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Configurar timeout más largo para procesar Mermaid
            page.set_default_timeout(45000)  # 45 segundos
            
            await page.set_content(full_html, wait_until='networkidle')
            
            # Esperar a que Mermaid renderice los diagramas
            self._log("⏳ Esperando renderizado de diagramas...")
            await asyncio.sleep(3)  # Tiempo adicional para Mermaid
            
            # Verificar si hay errores de Mermaid en el console
            page.on("console", lambda msg: 
                    self._log(f"🔍 Console: {msg.text}") if "mermaid" in msg.text.lower() else None)
            
            pdf_options = {
                'format': page_size,
                'margin': self._parse_margins(margins),
                'print_background': True,
                'path': str(output_file)
            }
            
            await page.pdf(**pdf_options)
            await browser.close()
        
        self._log(f"✅ PDF generado exitosamente: '{output_file}'")
        return output_file


def create_parser() -> argparse.ArgumentParser:
    """Crea el parser de argumentos."""
    parser = argparse.ArgumentParser(
        description='Convierte archivos Markdown a PDF con soporte para Mermaid',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python md_to_pdf.py documento.md
  python md_to_pdf.py documento.md -o informe.pdf
  python md_to_pdf.py documento.md --css-file estilos.css
  python md_to_pdf.py documento.md --page-size A5 --margins "10,15,10,15"
  python md_to_pdf.py documento.md --no-toc --quiet
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Archivo Markdown de entrada'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Archivo PDF de salida (por defecto: mismo nombre con .pdf)'
    )
    
    parser.add_argument(
        '--css-file',
        help='Archivo CSS personalizado para estilos'
    )
    
    parser.add_argument(
        '--page-size',
        default='A4',
        choices=['A4', 'A3', 'A5', 'Letter', 'Legal'],
        help='Tamaño de página (por defecto: A4)'
    )
    
    parser.add_argument(
        '--margins',
        default='20,20,20,20',
        help='Márgenes en formato "top,right,bottom,left" en mm (por defecto: 20,20,20,20)'
    )
    
    parser.add_argument(
        '--no-toc',
        action='store_true',
        help='Desactiva la generación de tabla de contenidos'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suprime los mensajes informativos'
    )
    
    return parser


async def main() -> int:
    """Función principal."""
    try:
        args = create_parser().parse_args()
        
        converter = MarkdownToPDFConverter(quiet=args.quiet)
        
        input_path = Path(args.input_file)
        output_path = Path(args.output) if args.output else None
        css_path = Path(args.css_file) if args.css_file else None
        
        await converter.convert(
            input_file=input_path,
            output_file=output_path,
            css_file=css_path,
            page_size=args.page_size,
            margins=args.margins,
            no_toc=args.no_toc
        )
        
        return 0
        
    except ImportError as e:
        print(f"Error: Dependencias faltantes: {e}", file=sys.stderr)
        print("Instale con: pip install playwright aiohttp && playwright install", file=sys.stderr)
        return 1
    except (FileNotFoundError, ValueError, UnicodeDecodeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error inesperado: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
    
       
# --- Ejemplos de uso ---

# Conversión básica: genera 'documento.pdf' a partir de 'documento.md'
# python md_to_pdf.py documento.md

# Especificar un archivo de salida diferente
# python md_to_pdf.py documento.md -o mi_informe.pdf

# Usar un archivo CSS personalizado
# python md_to_pdf.py documento.md --css-file estilos.css

# Cambiar el tamaño de página y los márgenes (formato: top,right,bottom,left)
# python md_to_pdf.py documento.md --page-size A5 --margins "10,15,10,15"

# Desactivar la tabla de contenidos (si la hay) y convertir en modo silencioso
# python md_to_pdf.py documento.md --no-toc --quiet

# Combinación de opciones
# python md_to_pdf.py lab.md -o laboratorio.pdf --page-size Letter --margins "25,25,25,25"

# python md_to_pdf.py sample_lab.md
# python md_to_pdf.py sample_prueba_emoji.md
# python md_to_pdf.py sample_test.md
# python md_to_pdf.py "C:\DevOps\MyGitHub\academia-docente\asignaturas\semestre-2\programacion-1-java\unidad-01-intro\lab-01-terminal-sin-ide\01-intro-terminal-java-sin-ide-lab.md"
# python md_to_pdf.py "C:\DevOps\MyGitHub\academia-docente\asignaturas\semestre-2\programacion-1-java\unidad-01-intro\lab-01-terminal-sin-ide\02-intro-terminal-java-sin-ide-informe.md"
# python md_to_pdf.py "C:\DevOps\MyGitHub\academia-docente\actividades\rompe-hielos\rompehielos-dos-verdades-una-mentira-tech.md"
# python md_to_pdf.py "C:\DevOps\MyGitHub\academia-docente\asignaturas\semestre-9\sistema-distribuido\actividades\saber-1\reportaje-tecnologico\actividad-reportaje.md"
# python md_to_pdf.py "C:\DevOps\MyGitHub\n8n-learning-journey\docs\deployments\n8n-local-env\README.md"


