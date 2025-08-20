#!/usr/bin/env python3
"""
Markdown to PDF Converter - Solo Playwright
==========================================

Script que convierte archivos Markdown (.md) a formato PDF
usando Playwright para soporte superior de emojis a color.

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
- Para instalar navegadores: `playwright install`
"""

import sys
import argparse
import markdown
import asyncio
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright

# CSS optimizado para emojis
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
    margin: 1em 0;
}

p {
    margin: 0.8em 0;
}

ul, ol {
    margin: 0.8em 0;
    padding-left: 1.5em;
}
"""


class MarkdownToPDFConverter:
    """Conversor simplificado de Markdown a PDF usando Playwright."""
    
    def __init__(self, quiet: bool = False):
        self.quiet = quiet
    
    def _log(self, message: str) -> None:
        """Imprime mensajes informativos si no está en modo silencioso."""
        if not self.quiet:
            print(message)
    
    def _load_file(self, file_path: Path) -> str:
        """Carga el contenido de un archivo Markdown."""
        try:
            return file_path.read_text(encoding='utf-8')
        except FileNotFoundError:
            raise FileNotFoundError(f"Archivo no encontrado: '{file_path}'")
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(f"Error de codificación en '{file_path}': {e}")
    
    def _markdown_to_html(self, md_content: str, enable_toc: bool = True) -> str:
        """Convierte contenido Markdown a HTML."""
        extensions = ['extra', 'codehilite', 'tables', 'fenced_code']
        if enable_toc:
            extensions.append('toc')
        
        return markdown.markdown(md_content, extensions=extensions, output_format='html5')
    
    def _get_css_content(self, css_file: Optional[Path]) -> str:
        """Obtiene CSS personalizado o el predeterminado."""
        if css_file and css_file.is_file():
            return self._load_file(css_file)
        return DEFAULT_CSS
    
    def _create_html_document(self, html_body: str, css_content: str, title: str) -> str:
        """Crea documento HTML completo."""
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{css_content}</style>
</head>
<body>
{html_body}
</body>
</html>"""
    
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
        
        self._log(f"Convirtiendo: '{input_file.name}' -> '{output_file.name}'")
        
        # Cargar y procesar contenido
        md_content = self._load_file(input_file)
        html_body = self._markdown_to_html(md_content, enable_toc=not no_toc)
        css_content = self._get_css_content(css_file)
        full_html = self._create_html_document(html_body, css_content, input_file.stem)
        
        # Generar PDF con Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            await page.set_content(full_html, wait_until='networkidle')
            
            pdf_options = {
                'format': page_size,
                'margin': self._parse_margins(margins),
                'print_background': True,
                'path': str(output_file)
            }
            
            await page.pdf(**pdf_options)
            await browser.close()
        
        self._log(f"✓ PDF generado exitosamente: '{output_file}'")
        return output_file


def create_parser() -> argparse.ArgumentParser:
    """Crea el parser de argumentos."""
    parser = argparse.ArgumentParser(
        description='Convierte archivos Markdown a PDF usando Playwright',
        formatter_class=argparse.RawDescriptionHelpFormatter
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
        
    except ImportError:
        print("Error: Playwright no está instalado.", file=sys.stderr)
        print("Instale con: pip install playwright && playwright install", file=sys.stderr)
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


