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
import sys
import zipfile
import argparse
import yaml
import logging
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

try:
    import py7zr
    HAS_PY7ZR = True
except ImportError:
    py7zr = None
    HAS_PY7ZR = False

class SevenZipHandler:
    """Maneja la detección y uso de 7-Zip (py7zr o aplicación instalada)."""
    
    def __init__(self, custom_path=None, logger=None):
        self.logger = logger
        self.custom_path = custom_path
        self.zip_executable = None
        self.method = None
        
        self._detect_7zip()
    
    def _detect_7zip(self):
        """Detecta qué método de 7-Zip usar."""
        # 1. Si py7zr está disponible, usarlo primero
        if HAS_PY7ZR:
            self.method = "py7zr"
            if self.logger:
                self.logger.debug("Usando py7zr para archivos 7z")
            return
        
        # 2. Buscar ejecutable 7z
        paths_to_check = []
        
        # Agregar ruta personalizada si se proporciona
        if self.custom_path:
            paths_to_check.append(self.custom_path)
        
        # Rutas comunes en Windows
        if os.name == 'nt':
            common_paths = [
                r"C:\Program Files\7-Zip\7z.exe",
                r"C:\Program Files (x86)\7-Zip\7z.exe",
                r"C:\Tools\7-Zip\7z.exe"
            ]
            paths_to_check.extend(common_paths)
        
        # Rutas comunes en Linux/Mac
        else:
            common_paths = [
                "/usr/bin/7z",
                "/usr/local/bin/7z",
                "/opt/local/bin/7z"
            ]
            paths_to_check.extend(common_paths)
        
        # Buscar en PATH del sistema
        path_executable = shutil.which("7z")
        if path_executable:
            paths_to_check.append(path_executable)
        
        # Probar cada ruta
        for path in paths_to_check:
            if self._test_7zip_executable(path):
                self.zip_executable = path
                self.method = "executable"
                if self.logger:
                    self.logger.info(f"Usando 7-Zip instalado: {path}")
                return
        
        # No se encontró ningún método
        self.method = None
        if self.logger:
            self.logger.warning("No se encontró py7zr ni 7-Zip instalado. Los archivos .7z no se procesarán.")
    
    def _test_7zip_executable(self, path):
        """Prueba si el ejecutable 7z funciona."""
        if not os.path.exists(path):
            return False
        
        try:
            result = subprocess.run(
                [path],
                capture_output=True,
                text=True,
                timeout=5
            )
            return True
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def can_extract_7z(self):
        """Retorna True si se puede extraer archivos 7z."""
        return self.method is not None
    
    def extract_7z_with_py7zr(self, file_path, output_dir):
        """Extrae usando py7zr."""
        with py7zr.SevenZipFile(file_path, mode='r') as z:
            z.extractall(output_dir)
    
    def extract_7z_with_executable(self, file_path, output_dir):
        """Extrae usando el ejecutable 7z."""
        cmd = [
            self.zip_executable,
            "x",  # extract with full paths
            str(file_path),
            f"-o{output_dir}",  # output directory
            "-y"  # assume Yes on all queries
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            raise Exception(f"7z failed with code {result.returncode}: {result.stderr}")
    
    def extract_7z(self, file_path, output_dir):
        """Extrae un archivo 7z usando el método disponible."""
        if self.method == "py7zr":
            self.extract_7z_with_py7zr(file_path, output_dir)
        elif self.method == "executable":
            self.extract_7z_with_executable(file_path, output_dir)
        else:
            raise Exception("No hay método disponible para extraer archivos 7z")

def setup_logging(log_file=None, verbose=False, quiet=False):
    """Configura el sistema de logging según los parámetros especificados."""
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    logger = logging.getLogger('bulk_extract')
    logger.setLevel(level)
    
    # Limpiar handlers existentes
    logger.handlers.clear()
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.info(f"Log guardándose en: {log_file}")
    
    return logger

def parse_arguments():
    """Configura y parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description='Descomprime masivamente archivos .zip y .7z de forma recursiva',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        help='Ruta del directorio donde buscar archivos comprimidos'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        help='Directorio base para las extracciones (default: misma ubicación del archivo)'
    )
    
    parser.add_argument(
        '--log-file',
        help='Archivo donde guardar el log de operaciones'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simula la extracción sin ejecutarla realmente'
    )
    
    parser.add_argument(
        '--remove-archives',
        action='store_true',
        help='Elimina los archivos originales después de extraer exitosamente'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        help='Profundidad máxima de búsqueda recursiva (0 = sin límite)'
    )
    
    parser.add_argument(
        '--include-extensions',
        help='Extensiones adicionales a procesar, separadas por comas (ej: .rar,.tar.gz)'
    )
    
    parser.add_argument(
        '--batch-config',
        help='Archivo YAML con configuraciones para procesamiento masivo'
    )
    
    parser.add_argument(
        '--7zip-path',
        help='Ruta personalizada al ejecutable 7z (ej: C:\\Program Files\\7-Zip\\7z.exe)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Modo silencioso, solo muestra errores críticos'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Modo detallado con información adicional de debug'
    )
    
    return parser.parse_args()

def get_supported_extensions(include_extensions=None):
    """Retorna las extensiones de archivo soportadas."""
    base_extensions = ['.zip', '.ZIP', '.7z', '.7Z']
    
    if include_extensions:
        additional = [ext.strip() for ext in include_extensions.split(',')]
        base_extensions.extend(additional)
    
    return base_extensions

def find_archives(directory_path, extensions, max_depth=None, logger=None):
    """Busca archivos comprimidos en el directorio especificado."""
    path = Path(directory_path)
    found_files = []
    
    def search_recursive(current_path, current_depth=0):
        if max_depth is not None and current_depth > max_depth:
            return
        
        try:
            for item in current_path.iterdir():
                if item.is_file():
                    if any(item.name.endswith(ext) for ext in extensions):
                        found_files.append(item)
                        if logger:
                            logger.debug(f"Encontrado: {item}")
                elif item.is_dir():
                    search_recursive(item, current_depth + 1)
        except PermissionError:
            if logger:
                logger.warning(f"Sin permisos para acceder a: {current_path}")
        except Exception as e:
            if logger:
                logger.error(f"Error al buscar en {current_path}: {e}")
    
    search_recursive(path)
    return sorted(found_files)

def extract_zip(file_path, output_dir, dry_run=False, logger=None):
    """Extrae un archivo ZIP."""
    try:
        if dry_run:
            if logger:
                logger.info(f"[DRY RUN] Extraería: {file_path} → {output_dir}")
            return True
        
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        
        if logger:
            logger.info(f"✓ Extraído: {file_path.name} → {output_dir.name}/")
        return True
        
    except zipfile.BadZipFile:
        if logger:
            logger.error(f"✗ Archivo ZIP corrupto: {file_path}")
        return False
    except Exception as e:
        if logger:
            logger.error(f"✗ Error al extraer {file_path}: {e}")
        return False

def extract_7z(file_path, output_dir, seven_zip_handler, dry_run=False, logger=None):
    """Extrae un archivo 7z usando SevenZipHandler."""
    if not seven_zip_handler.can_extract_7z():
        if logger:
            logger.error(f"✗ No se puede extraer {file_path}: No hay método 7z disponible")
        return False
    
    try:
        if dry_run:
            if logger:
                logger.info(f"[DRY RUN] Extraería: {file_path} → {output_dir}")
            return True
        
        seven_zip_handler.extract_7z(file_path, output_dir)
        
        if logger:
            logger.info(f"✓ Extraído: {file_path.name} → {output_dir.name}/")
        return True
        
    except Exception as e:
        if logger:
            logger.error(f"✗ Error al extraer {file_path}: {e}")
        return False

def extract_archive(file_path, base_output_dir=None, seven_zip_handler=None, dry_run=False, logger=None):
    """Extrae un archivo según su extensión."""
    # Determinar directorio de salida
    if base_output_dir:
        output_dir = Path(base_output_dir) / file_path.stem
    else:
        output_dir = file_path.parent / file_path.stem
    
    # Crear directorio si no existe (excepto en dry-run)
    if not dry_run:
        output_dir.mkdir(exist_ok=True)
    
    # Determinar tipo de archivo y extraer
    file_ext = file_path.suffix.lower()
    
    if file_ext == '.zip':
        return extract_zip(file_path, output_dir, dry_run, logger)
    elif file_ext == '.7z':
        return extract_7z(file_path, output_dir, seven_zip_handler, dry_run, logger)
    else:
        if logger:
            logger.warning(f"Tipo de archivo no soportado: {file_path}")
        return False

def bulk_extract(directory, output_dir=None, max_depth=None, include_extensions=None, 
                dry_run=False, remove_archives=False, seven_zip_path=None, logger=None):
    """Función principal que ejecuta la extracción masiva."""
    path = Path(directory)
    
    # Validar directorio
    if not path.exists():
        raise FileNotFoundError(f"El directorio '{directory}' no existe")
    
    if not path.is_dir():
        raise NotADirectoryError(f"'{directory}' no es un directorio")
    
    # Inicializar handler de 7-Zip
    seven_zip_handler = SevenZipHandler(seven_zip_path, logger)
    
    # Obtener extensiones soportadas
    extensions = get_supported_extensions(include_extensions)
    
    if logger:
        logger.info(f"Iniciando búsqueda en: {path.absolute()}")
        logger.info(f"Extensiones a procesar: {extensions}")
        if max_depth is not None:
            logger.info(f"Profundidad máxima: {max_depth} niveles")
        if dry_run:
            logger.info("MODO DRY RUN: No se realizarán extracciones reales")
    
    # Buscar archivos
    archive_files = find_archives(directory, extensions, max_depth, logger)
    
    if not archive_files:
        if logger:
            logger.info("No se encontraron archivos comprimidos para procesar")
        return 0, 0
    
    # Clasificar archivos por tipo
    zip_files = [f for f in archive_files if f.suffix.lower() == '.zip']
    z7_files = [f for f in archive_files if f.suffix.lower() == '.7z']
    other_files = [f for f in archive_files if f not in zip_files and f not in z7_files]
    
    total_files = len(archive_files)
    
    if logger:
        logger.info(f"Encontrados {len(zip_files)} archivos ZIP, {len(z7_files)} archivos 7z, {len(other_files)} otros")
        logger.info("=" * 60)
    
    # Procesar archivos
    success_count = 0
    
    for archive_file in archive_files:
        success = extract_archive(
            archive_file, 
            output_dir, 
            seven_zip_handler,
            dry_run, 
            logger
        )
        
        if success:
            success_count += 1
            
            # Eliminar archivo original si se especifica
            if remove_archives and not dry_run:
                try:
                    archive_file.unlink()
                    if logger:
                        logger.info(f"Eliminado archivo original: {archive_file.name}")
                except Exception as e:
                    if logger:
                        logger.error(f"Error al eliminar {archive_file}: {e}")
    
    if logger:
        logger.info("=" * 60)
        logger.info(f"Proceso completado: {success_count}/{total_files} archivos procesados correctamente")
    
    return success_count, total_files

def run_batch(batch_file, logger=None):
    """Ejecuta el procesamiento masivo basado en un archivo de configuración YAML."""
    try:
        if not os.path.exists(batch_file):
            raise FileNotFoundError(f"El archivo de configuración batch no existe: {batch_file}")
        
        with open(batch_file, 'r', encoding='utf-8') as f:
            batch_config = yaml.safe_load(f)
        
        extractions = batch_config.get('extractions', [])
        if not extractions:
            if logger:
                logger.error("No se encontraron configuraciones de extracción en el archivo batch")
            return
        
        if logger:
            logger.info(f"Iniciando procesamiento masivo de {len(extractions)} configuración(es)...")
            logger.info("=" * 60)
        
        total_success = 0
        total_files = 0
        
        for i, extraction in enumerate(extractions, 1):
            # Validar campos requeridos
            path = extraction.get('path')
            if not path:
                if logger:
                    logger.error(f"Error en configuración {i}: Falta el campo 'path'")
                continue
            
            # Campos opcionales con valores por defecto
            output_dir = extraction.get('output_dir')
            max_depth = extraction.get('max_depth')
            include_extensions = extraction.get('include_extensions')
            dry_run = extraction.get('dry_run', False)
            remove_archives = extraction.get('remove_archives', False)
            config_log_file = extraction.get('log_file')
            seven_zip_path = extraction.get('7zip_path')
            
            if logger:
                logger.info(f"\n[{i}/{len(extractions)}] Procesando configuración:")
                logger.info(f"  - Ruta: {path}")
                logger.info(f"  - Directorio salida: {output_dir or 'Misma ubicación'}")
                logger.info(f"  - Profundidad máxima: {max_depth or 'Sin límite'}")
                logger.info(f"  - Dry run: {'Sí' if dry_run else 'No'}")
                logger.info(f"  - Eliminar originales: {'Sí' if remove_archives else 'No'}")
                if seven_zip_path:
                    logger.info(f"  - Ruta 7z personalizada: {seven_zip_path}")
            
            # Configurar logger específico si se especifica
            config_logger = logger
            if config_log_file:
                config_logger = setup_logging(config_log_file, verbose=False, quiet=False)
            
            try:
                success, total = bulk_extract(
                    path,
                    output_dir=output_dir,
                    max_depth=max_depth,
                    include_extensions=include_extensions,
                    dry_run=dry_run,
                    remove_archives=remove_archives,
                    seven_zip_path=seven_zip_path,
                    logger=config_logger
                )
                
                total_success += success
                total_files += total
                
                if logger:
                    logger.info(f"  ✓ Configuración {i} completada: {success}/{total} archivos")
                    
            except Exception as e:
                if logger:
                    logger.error(f"  ✗ Error al procesar configuración {i}: {str(e)}")
                continue
        
        if logger:
            logger.info("\n" + "=" * 60)
            logger.info(f"Procesamiento masivo completado: {total_success}/{total_files} archivos totales")
        
    except Exception as e:
        if logger:
            logger.error(f"Error en el procesamiento masivo: {e}")
        raise

def main():
    """Función principal que ejecuta el programa."""
    try:
        # Parsear argumentos
        args = parse_arguments()
        
        # Configurar logging
        logger = setup_logging(args.log_file, args.verbose, args.quiet)
        
        # Validar argumentos
        if args.batch_config:
            # Modo batch
            if args.path:
                logger.warning("El argumento 'path' será ignorado al usar --batch-config")
            run_batch(args.batch_config, logger)
        else:
            # Modo individual
            if not args.path:
                logger.error("Error: Debe especificar una ruta o usar --batch-config para procesamiento masivo")
                return 1
            
            success, total = bulk_extract(
                args.path,
                output_dir=args.output_dir,
                max_depth=args.max_depth,
                include_extensions=args.include_extensions,
                dry_run=args.dry_run,
                remove_archives=args.remove_archives,
                seven_zip_path=getattr(args, '7zip_path', None),
                logger=logger
            )
            
            if not args.quiet:
                if success == total:
                    logger.info("¡Todos los archivos se procesaron exitosamente!")
                else:
                    logger.warning(f"Se procesaron {success} de {total} archivos. Revisa los errores arriba.")
        
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}")
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
# python bulk-extract.py "C:\Users\ronald.cuello\Downloads\parcial\PROGRAMACIÓN I (CLASE 2557) TDSOF-2561-Parcial II Programacion orientada a objetos-1717365" --7zip-path "C:\Program Files\7-Zip\7z.exe"

# Con opciones avanzadas
# python bulk-extract.py /ruta/de/archivos --log-file operations.log --remove-archives --max-depth 3