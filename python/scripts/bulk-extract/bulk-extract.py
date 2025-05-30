#!/usr/bin/env python3
"""
Bulk Archive Extractor
======================

Este script descomprime masivamente archivos .zip y .7z de forma recursiva en 
cualquier directorio y sus subcarpetas, ideal para tareas DevOps y automatización.

Uso básico:
-----------
    python bulk-extract.py /ruta/del/directorio

Argumentos disponibles:
----------------------
    path                        Ruta del directorio a procesar (obligatorio)
    -o, --output-dir           Directorio base para extracciones (default: misma ubicación)
    --log-file                 Archivo de log para registrar operaciones
    --dry-run                  Simula la extracción sin ejecutarla
    --remove-archives          Elimina archivos originales después de extraer
    --max-depth               Profundidad máxima de búsqueda (0 = sin límite)
    --include-extensions      Extensiones adicionales a procesar (ej: .rar,.tar.gz)
    --batch-config            Archivo YAML con configuraciones para procesamiento masivo
    --quiet                   Modo silencioso, solo errores críticos
    -v, --verbose             Modo detallado con información adicional
    --7zip-path               Ruta personalizada al ejecutable 7z (ej: C:\Program Files\7-Zip\7z.exe)
    -h, --help               Muestra este mensaje de ayuda

Ejemplos de uso:
---------------
1. Extraer todos los archivos en un directorio:
    python bulk-extract.py /ruta/de/archivos

2. Simular extracción sin ejecutar:
    python bulk-extract.py /ruta/de/archivos --dry-run

3. Extraer y eliminar archivos originales:
    python bulk-extract.py /ruta/de/archivos --remove-archives

4. Guardar log de operaciones:
    python bulk-extract.py /ruta/de/archivos --log-file extraction.log

5. Extraer solo hasta 2 niveles de profundidad:
    python bulk-extract.py /ruta/de/archivos --max-depth 2

6. Usar 7-Zip instalado en ruta personalizada:
    python bulk-extract.py /ruta/de/archivos --7zip-path "C:\Program Files\7-Zip\7z.exe"

7. Procesamiento masivo usando archivo de configuración:
    python bulk-extract.py --batch-config extract_batch_config.yaml

Formato del archivo batch config:
-------------------------------
extractions:
  - path: /var/backups/daily
    output_dir: /var/extracted/daily
    remove_archives: false
    max_depth: 3
    log_file: daily_extraction.log
    zip_path: "C:\Program Files\7-Zip\7z.exe"
  - path: /var/backups/weekly
    output_dir: /var/extracted/weekly
    remove_archives: true
    max_depth: 1

Salida de ejemplo:
----------------
Encontrados 3 archivos ZIP y 2 archivos 7z (búsqueda recursiva)
Directorio de trabajo: /home/user/deployment-files
Profundidad máxima: 2 niveles
Usando 7-Zip instalado: C:\Program Files\7-Zip\7z.exe
------------------------------------------------------------
✓ Extraído: frontend-v2.1.zip → frontend-v2.1/
✓ Extraído: api/backend-service.zip → api/backend-service/
✗ Error al extraer corrupted-file.zip: Bad zipfile
✓ Extraído: database/backup-2024.7z → database/backup-2024/
✓ Extraído: configs/settings.7Z → configs/settings/
------------------------------------------------------------
Proceso completado: 4/5 archivos extraídos correctamente.

Autor: DevOps Team
Versión: 2.1.0
Fecha: 2025-05-29
"""

import os
import argparse
import yaml
import fnmatch
import logging
from pathlib import Path
from datetime import datetime

def setup_logging(verbose=False, quiet=False):
    """
    Configura el sistema de logging basado en las opciones del usuario.
    """
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    # Formato simple y claro
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configurar logger principal
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(console_handler)
    
    return logger

def parse_arguments():
    """
    Configura y parsea los argumentos de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description='Genera un árbol de directorios en formato texto',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Hacer path opcional cuando se usa batch-config
    parser.add_argument(
        'path',
        nargs='?',  # Hacer opcional
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

    parser.add_argument(
        '--batch-config',
        help='Archivo YAML con configuraciones para escaneo masivo'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Habilita logging detallado (DEBUG)'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Silencia la salida (solo errores)'
    )
    
    return parser.parse_args()

def load_ignore_patterns(ignore_file):
    """
    Carga los patrones de ignore desde el archivo YAML.
    """
    logger = logging.getLogger(__name__)
    
    try:
        if os.path.exists(ignore_file):
            logger.info(f"Cargando archivo ignore: {ignore_file}")
            with open(ignore_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                ignore_dirs = set(config.get('ignore_directories', []))
                ignore_files = set(config.get('ignore_files', []))
                logger.debug(f"Directorios a ignorar: {ignore_dirs}")
                logger.debug(f"Archivos a ignorar: {ignore_files}")
                return ignore_dirs, ignore_files
        else:
            logger.warning(f"Archivo ignore no encontrado: {ignore_file}")
    except Exception as e:
        logger.error(f"Error al cargar {ignore_file}: {str(e)}")
    
    return set(), set()

def should_ignore(entry, ignore_dirs, ignore_files):
    """
    Determina si una entrada debe ser ignorada según los patrones.
    """
    logger = logging.getLogger(__name__)
    name = entry.name
    
    if entry.is_dir():
        should_ignore_dir = any(fnmatch.fnmatch(name, pattern) for pattern in ignore_dirs)
        if should_ignore_dir:
            logger.debug(f"Ignorando directorio: {name}")
        return should_ignore_dir
    else:
        should_ignore_file = any(fnmatch.fnmatch(name, pattern) for pattern in ignore_files)
        if should_ignore_file:
            logger.debug(f"Ignorando archivo: {name}")
        return should_ignore_file

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
    logger = logging.getLogger(__name__)
    
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
            logger.warning(f"Permiso denegado para acceder a: {path}")
            file.write(f"{prefix}!-- Permiso denegado --!\n")
        except Exception as e:
            logger.error(f"Error al procesar {path}: {str(e)}")
            file.write(f"{prefix}!-- Error: {str(e)} --!\n")

    # Crear el objeto Path para manejar rutas
    root = Path(root_path).resolve()
    
    # Verificar que el directorio existe
    if not root.exists():
        raise FileNotFoundError(f"El directorio {root_path} no existe")
    
    logger.info(f"Escaneando directorio: {root}")
    logger.info(f"Usando archivo ignore: {ignore_file}")
    
    # Abrir archivo de salida
    with open(output_file, 'w', encoding='utf-8') as f:
        # Agregar metadata al archivo
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"# Estructura de directorios generada el {timestamp}\n")
        f.write(f"# Directorio escaneado: {root}\n")
        f.write(f"# Archivo ignore utilizado: {ignore_file}\n")
        f.write(f"# Solo directorios: {'Sí' if no_files else 'No'}\n")
        f.write(f"# Profundidad máxima: {'Sin límite' if max_depth is None else max_depth}\n")
        f.write(f"{'='*60}\n\n")
        
        f.write(f"{root.name}/\n")
        write_tree(f, root)

def run_batch(batch_file):
    """
    Ejecuta el escaneo masivo basado en un archivo de configuración YAML.
    """
    logger = logging.getLogger(__name__)
    
    try:
        if not os.path.exists(batch_file):
            raise FileNotFoundError(f"El archivo de configuración batch no existe: {batch_file}")
        
        with open(batch_file, 'r', encoding='utf-8') as f:
            batch_config = yaml.safe_load(f)
        
        projects = batch_config.get('projects', [])
        if not projects:
            logger.error("No se encontraron proyectos en el archivo de configuración batch")
            return
        
        logger.info(f"Iniciando escaneo masivo de {len(projects)} proyecto(s)...")
        
        for i, project in enumerate(projects, 1):
            # Validar campos requeridos
            path = project.get('path')
            if not path:
                logger.error(f"Error en proyecto {i}: Falta el campo 'path'")
                continue
            
            # Campos opcionales con valores por defecto
            ignore_file = project.get('ignore_file', 'ignore.yml')
            output = project.get('output', f'estructura_proyecto_{i}.txt')
            no_files = project.get('no_files', False)
            max_depth = project.get('max_depth')  # None si no se especifica
            
            logger.info(f"[{i}/{len(projects)}] Procesando proyecto: {path}")
            logger.debug(f"  - Archivo ignore: {ignore_file}")
            logger.debug(f"  - Archivo salida: {output}")
            logger.debug(f"  - Solo directorios: {'Sí' if no_files else 'No'}")
            logger.debug(f"  - Profundidad máxima: {'Sin límite' if max_depth is None else max_depth}")
            
            try:
                scan_directory(
                    path,
                    output,
                    ignore_file=ignore_file,
                    no_files=no_files,
                    max_depth=max_depth
                )
                logger.info(f"  ✓ Estructura guardada exitosamente en: {output}")
            except Exception as e:
                logger.error(f"  ✗ Error al procesar proyecto {i}: {str(e)}")
                continue
        
        logger.info("Escaneo masivo completado")
        
    except Exception as e:
        logger.error(f"Error en el escaneo masivo: {e}")
        raise

def main():
    """Función principal que ejecuta el programa."""
    try:
        # Parsear argumentos
        args = parse_arguments()
        
        # Configurar logging
        logger = setup_logging(verbose=args.verbose, quiet=args.quiet)

        # Validar argumentos
        if args.batch_config:
            # Modo batch
            if args.path:
                logger.warning("El argumento 'path' será ignorado al usar --batch-config")
            run_batch(args.batch_config)
        else:
            # Modo individual
            if not args.path:
                logger.error("Debe especificar una ruta o usar --batch-config para escaneo masivo")
                return 1
            
            scan_directory(
                args.path,
                args.output,
                ignore_file=args.ignore_file,
                no_files=args.no_files,
                max_depth=args.max_depth
            )
            logger.info(f"Estructura guardada exitosamente en: {args.output}")
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

# Ejemplos de uso comentados:
# python bulk-extract.py /var/backups/compressed
# python bulk-extract.py /var/backups/compressed --log-file extraction.log
# python bulk-extract.py /var/backups/compressed --dry-run --verbose
# python bulk-extract.py /var/backups/compressed --remove-archives --max-depth 2
# python bulk-extract.py /var/backups/compressed -o /var/extracted --include-extensions .rar,.tar.gz
# python bulk-extract.py /var/backups/compressed --7zip-path "C:\Program Files\7-Zip\7z.exe"
# python bulk-extract.py --batch-config extract_batch_config.yaml

# Uso básico
# python bulk-extract.py /ruta/de/archivos
# python bulk-extract.py "C:\Ruta\de\archivos" --7zip-path "C:\Program Files\7-Zip\7z.exe"

# Con opciones avanzadas
# python bulk-extract.py /ruta/de/archivos --log-file operations.log --remove-archives --max-depth 3