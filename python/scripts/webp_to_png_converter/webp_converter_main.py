#!/usr/bin/env python3
"""
Script ejecutor para la clase WebpToPngConverter.
Permite convertir archivos WEBP a PNG desde la línea de comandos.
"""

import argparse
import os
import sys
from webp_to_png_converter import WebpToPngConverter

def parse_args():
    """Configura y parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description='Convierte archivos WEBP a formato PNG'
    )
    
    # Grupo de argumentos mutuamente excluyentes
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', help='Ruta al archivo WEBP a convertir')
    group.add_argument('-d', '--directory', help='Directorio con archivos WEBP a convertir')
    
    # Argumentos opcionales
    parser.add_argument('-o', '--output', help='Ruta o directorio de salida para los archivos PNG')
    parser.add_argument('-v', '--verbose', action='store_true', help='Mostrar información detallada')
    
    return parser.parse_args()

def main():
    """Función principal del script."""
    args = parse_args()
    
    # Crear instancia del conversor
    converter = WebpToPngConverter()
    
    try:
        if args.file:
            # Verificar que el archivo existe
            if not os.path.isfile(args.file):
                print(f"Error: El archivo '{args.file}' no existe.")
                sys.exit(1)
                
            # Verificar que el archivo es WEBP
            if not args.file.lower().endswith('.webp'):
                print(f"Error: El archivo '{args.file}' no parece ser un archivo WEBP.")
                sys.exit(1)
                
            # Convertir archivo individual
            output_path = converter.convert(args.file, args.output)
            print(f"Conversión exitosa: {output_path}")
            
        elif args.directory:
            # Verificar que el directorio existe
            if not os.path.isdir(args.directory):
                print(f"Error: El directorio '{args.directory}' no existe.")
                sys.exit(1)
                
            # Convertir todos los archivos en el directorio
            converted_files = converter.convert_directory(args.directory, args.output)
            
            if converted_files:
                print(f"Conversión exitosa de {len(converted_files)} archivos:")
                if args.verbose:
                    for file in converted_files:
                        print(f"  - {file}")
            else:
                print("No se encontraron archivos WEBP para convertir.")
    
    except Exception as e:
        print(f"Error durante la conversión: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Para convertir un solo archivo
# python webp_converter_main.py -f imagen.webp

# Para convertir un archivo y especificar la salida
# python webp_converter_main.py -f imagen.webp -o salida/imagen_convertida.png

# Para convertir todos los archivos WEBP en un directorio
# python webp_converter_main.py -d carpeta_con_webps

# Para convertir un directorio y especificar el directorio de salida
# python webp_converter_main.py -d carpeta_con_webps -o carpeta_de_salida

# Para ver información detallada sobre los archivos convertidos
# python webp_converter_main.py -d carpeta_con_webps -v

# Para convertir un directorio y especificar el directorio de salida
# python webp_converter_main.py -d "C:\Users\ronald.cuello\Downloads\DALLE webp Images\convert" -o "C:\Users\ronald.cuello\Downloads\DALLE webp Images\converted"