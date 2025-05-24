import os
import argparse
import yaml
import fnmatch
from pathlib import Path
from datetime import datetime

def parse_arguments():
    """
    Configura y parsea los argumentos de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description='Genera un árbol de directorios en formato texto',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        'path',
        help='Ruta del directorio a escanear'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='estructura_directorios.txt',
        help='Archivo de salida donde se guardará la estructura'
    )
    
    parser.add_argument(
        '--ignore-file',
        default='ignore.yml',
        help='Archivo YAML con patrones para ignorar'
    )
    
    parser.add_argument(
        '--no-files',
        action='store_true',
        help='Excluye los archivos, mostrando solo directorios'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        help='Profundidad máxima del árbol (0 = sin límite)'
    )
    
    return parser.parse_args()

def load_ignore_patterns(ignore_file):
    """
    Carga los patrones de ignore desde el archivo YAML.
    """
    try:
        if os.path.exists(ignore_file):
            print(f"Cargando archivo ignore: {ignore_file}")
            with open(ignore_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                ignore_dirs = set(config.get('ignore_directories', []))
                ignore_files = set(config.get('ignore_files', []))
                print(f"Directorios a ignorar: {ignore_dirs}")
                print(f"Archivos a ignorar: {ignore_files}")
                return ignore_dirs, ignore_files
        else:
            print(f"Archivo ignore no encontrado: {ignore_file}")
    except Exception as e:
        print(f"Error al cargar {ignore_file}: {str(e)}")
    
    return set(), set()

def should_ignore(entry, ignore_dirs, ignore_files):
    """
    Determina si una entrada debe ser ignorada según los patrones.
    """
    name = entry.name
    
    if entry.is_dir():
        should_ignore = any(fnmatch.fnmatch(name, pattern) for pattern in ignore_dirs)
        if should_ignore:
            print(f"Ignorando directorio: {name}")
        return should_ignore
    else:
        should_ignore = any(fnmatch.fnmatch(name, pattern) for pattern in ignore_files)
        if should_ignore:
            print(f"Ignorando archivo: {name}")
        return should_ignore

def get_tree_chars(is_last):
    """
    Retorna los caracteres correctos para el árbol según si es el último elemento.
    """
    if is_last:
        return "└── ", "    "
    return "├── ", "│   "

def scan_directory(root_path, output_file, ignore_file='ignore.yml', no_files=False, max_depth=None):
    """
    Escanea la estructura de directorios y genera un árbol en formato texto.
    """
    # Cargar patrones de ignore
    ignore_dirs, ignore_files = load_ignore_patterns(ignore_file)
    
    def write_tree(file, path, prefix="", current_depth=0):
        if max_depth is not None and current_depth > max_depth:
            return
            
        # Filtrar entradas según los patrones de ignore
        try:
            entries = path.iterdir()
            filtered_entries = []
            for entry in sorted(entries, key=lambda x: (not x.is_dir(), x.name.lower())):
                if not should_ignore(entry, ignore_dirs, ignore_files):
                    filtered_entries.append(entry)
                
            entries = filtered_entries
            
            if no_files:
                entries = [e for e in entries if e.is_dir()]
                
            for i, entry in enumerate(entries):
                is_last = i == len(entries) - 1
                current_prefix, child_prefix = get_tree_chars(is_last)
                
                file.write(f"{prefix}{current_prefix}{entry.name}")
                if entry.is_dir():
                    file.write("/\n")
                    write_tree(file, entry, prefix + child_prefix, current_depth + 1)
                else:
                    file.write("\n")
        except PermissionError:
            file.write(f"{prefix}!-- Permiso denegado --!\n")
        except Exception as e:
            file.write(f"{prefix}!-- Error: {str(e)} --!\n")

    # Crear el objeto Path para manejar rutas
    root = Path(root_path).resolve()
    
    # Verificar que el directorio existe
    if not root.exists():
        raise FileNotFoundError(f"El directorio {root_path} no existe")
    
    print(f"\nEscaneando directorio: {root}")
    print(f"Usando archivo ignore: {ignore_file}\n")
    
    # Abrir archivo de salida
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"{root.name}/\n")
        write_tree(f, root)

def main():
    """Función principal que ejecuta el programa."""
    try:
        # Parsear argumentos
        args = parse_arguments()
        
        # Ejecutar el escaneo
        scan_directory(
            args.path,
            args.output,
            ignore_file=args.ignore_file,
            no_files=args.no_files,
            max_depth=args.max_depth
        )
        
        print(f"\nEstructura guardada exitosamente en: {args.output}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

# python scan_directory.py C:\DevOps\MarketPlace\mpt-public-catalog\worker -o worker.txt
# python scan_directory.py C:\DevOps\MarketPlace\mpt-public-catalog\worker -o worker.txt --ignore-file C:\DevOps\MarketPlace\py-utils\scan_ignore.yaml

# Uso básico (busca ignore.yml en el directorio actual)
# python scan_directory.py /ruta/del/proyecto

# Especificar un archivo ignore diferente
# python scan_directory.py /ruta/del/proyecto --ignore-file mi_ignore.yml
# python scan_directory.py "C:\DevOps\MyGitHub\Udemy\amazonashop" --ignore-file "C:\DevOps\MarketPlace\py-utils\scan_ignore.yaml"
# python scan_directory.py "C:\DevOps\MyGitHub\Udemy\amazonashop\QA\tests\performance" --ignore-file "C:\DevOps\MarketPlace\py-utils\scan_ignore.yaml"


#!/usr/bin/env python3
"""
Directory Tree Generator
=======================

Este script genera una representación en árbol de la estructura de directorios,
similar al comando 'tree' en sistemas Unix, con soporte para ignorar archivos
y directorios específicos mediante un archivo de configuración YAML.

Uso básico:
-----------
    python scan_directory.py /ruta/del/proyecto

Argumentos disponibles:
----------------------
    path                        Ruta del directorio a escanear (obligatorio)
    -o, --output               Archivo de salida (default: estructura_directorios.txt)
    --ignore-file             Archivo YAML con patrones para ignorar (default: ignore.yml)
    --no-files                Excluye los archivos, muestra solo directorios
    --max-depth               Profundidad máxima del árbol (0 = sin límite)
    -h, --help               Muestra este mensaje de ayuda

Ejemplos de uso:
---------------
1. Escanear un directorio con configuración por defecto:
    python scan_directory.py /ruta/del/proyecto

2. Especificar archivo de salida personalizado:
    python scan_directory.py /ruta/del/proyecto -o mi_estructura.txt

3. Usar un archivo ignore personalizado:
    python scan_directory.py /ruta/del/proyecto --ignore-file mi_ignore.yml

4. Mostrar solo directorios hasta una profundidad de 2 niveles:
    python scan_directory.py /ruta/del/proyecto --no-files --max-depth 2

Formato del archivo ignore.yml:
-----------------------------
ignore_directories:          # Carpetas a ignorar
  - node_modules
  - .git
  - bin
  - obj

ignore_files:               # Archivos a ignorar (soporta patrones glob)
  - "*.log"
  - "*.tmp"
  - ".DS_Store"

Salida de ejemplo:
----------------
MiProyecto/
├── src/
│   ├── controllers/
│   │   └── UserController.cs
│   └── models/
│       └── User.cs
├── tests/
│   └── UserTests.cs
└── README.md

Autor: X
Versión: 1.0.0
Fecha: 2025-01-15
"""