#!/usr/bin/env python3
"""
Graylog Connectivity Checker
===========================

Este script verifica la conectividad con un servidor Graylog probando
múltiples componentes y enviando mensajes de prueba para confirmar
que todos los servicios están funcionando correctamente.

Uso básico:
-----------
    python graylog_checker.py

Argumentos disponibles:
----------------------
    --host                     Host de Graylog (default: localhost)
    --config                   Archivo YAML con configuración personalizada
    --timeout                  Timeout para conexiones en segundos (default: 5)
    --verbose                  Mostrar información detallada de las pruebas
    --output                   Archivo para guardar el reporte (opcional)
    -h, --help                Muestra este mensaje de ayuda

Ejemplos de uso:
---------------
1. Verificación básica en localhost:
    python graylog_checker.py

2. Verificar servidor remoto:
    python graylog_checker.py --host graylog.miempresa.com

3. Usar configuración personalizada:
    python graylog_checker.py --config mi_graylog.yml

4. Generar reporte detallado:
    python graylog_checker.py --verbose --output reporte_graylog.txt

Formato del archivo de configuración YAML:
-----------------------------------------
host: "localhost"
timeout: 5
ports:
  web: 9001
  syslog_udp: 1514
  gelf_udp: 12201
  opensearch: 9200

test_messages:
  syslog:
    facility: "test-server"
    message: "Mensaje de prueba Syslog personalizado"
  gelf:
    host: "ecommerce-app"
    short_message: "Order placed successfully"
    full_message: "Customer John Doe placed order #12345"

Salida de ejemplo:
----------------
🔍 Probando Graylog en localhost...
────────────────────────────────────────
✅ Web interface: OK (Status: 200)
✅ OpenSearch: OK (Status: green)
✅ Syslog UDP: Mensaje enviado
✅ GELF UDP: Mensaje enviado
────────────────────────────────────────
🎉 TODAS LAS PRUEBAS PASARON (4/4)
✅ Graylog está funcionando correctamente

Autor: Assistant
Versión: 2.0.0
Fecha: 2025-05-29
"""

import json
import socket
import time
import requests
import argparse
import yaml
import os
from datetime import datetime
from pathlib import Path

def parse_arguments():
    """
    Configura y parsea los argumentos de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description='Verifica la conectividad con servidor Graylog',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--host',
        default='localhost',
        help='Host del servidor Graylog'
    )
    
    parser.add_argument(
        '--config',
        help='Archivo YAML con configuración personalizada'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=5,
        help='Timeout para conexiones en segundos'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mostrar información detallada de las pruebas'
    )
    
    parser.add_argument(
        '--output',
        help='Archivo para guardar el reporte de conectividad'
    )
    
    return parser.parse_args()

def load_config(config_file, host, timeout):
    """
    Carga la configuración desde archivo YAML o usa valores por defecto.
    """
    default_config = {
        'host': host,
        'timeout': timeout,
        'ports': {
            'web': 9001,
            'syslog_udp': 1514,
            'gelf_udp': 12201,
            'opensearch': 9200
        },
        'test_messages': {
            'syslog': {
                'facility': 'test-server',
                'message': 'Mensaje de prueba Syslog'
            },
            'gelf': {
                'host': 'ecommerce-app',
                'short_message': 'Order placed successfully',
                'full_message': 'Customer John Doe placed order #12345 for $120.99'
            }
        }
    }
    
    if config_file and os.path.exists(config_file):
        try:
            print(f"Cargando configuración desde: {config_file}")
            with open(config_file, 'r', encoding='utf-8') as f:
                custom_config = yaml.safe_load(f)
                # Merge configs (custom overrides default)
                for key, value in custom_config.items():
                    if isinstance(value, dict) and key in default_config:
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
            print("Usando configuración por defecto")
    
    return default_config

def test_web_interface(config, verbose=False):
    """
    Prueba si la interfaz web de Graylog responde.
    """
    test_name = "Web Interface"
    try:
        url = f"http://{config['host']}:{config['ports']['web']}/api/system"
        if verbose:
            print(f"  Probando URL: {url}")
        
        response = requests.get(url, timeout=config['timeout'])
        message = f"✅ {test_name}: OK (Status: {response.status_code})"
        print(message)
        return True, message
    except Exception as e:
        message = f"❌ {test_name}: FAILED"
        if verbose:
            message += f" - {str(e)}"
        print(message)
        return False, message

def test_opensearch(config, verbose=False):
    """
    Prueba si OpenSearch responde correctamente.
    """
    test_name = "OpenSearch"
    try:
        url = f"http://{config['host']}:{config['ports']['opensearch']}/_cluster/health"
        if verbose:
            print(f"  Probando URL: {url}")
        
        response = requests.get(url, timeout=config['timeout'])
        health_status = response.json().get('status', 'unknown')
        message = f"✅ {test_name}: OK (Status: {health_status})"
        print(message)
        return True, message
    except Exception as e:
        message = f"❌ {test_name}: FAILED"
        if verbose:
            message += f" - {str(e)}"
        print(message)
        return False, message

def test_syslog_udp(config, verbose=False):
    """
    Envía mensaje de prueba vía Syslog UDP.
    """
    test_name = "Syslog UDP"
    try:
        host = config['host']
        port = config['ports']['syslog_udp']
        
        if verbose:
            print(f"  Enviando a {host}:{port}")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(config['timeout'])
        
        timestamp = datetime.now().strftime('%b %d %H:%M:%S')
        facility = config['test_messages']['syslog']['facility']
        msg_text = config['test_messages']['syslog']['message']
        message = f"<134>{timestamp} {facility} graylog-test: {msg_text}"
        
        sock.sendto(message.encode(), (host, port))
        sock.close()
        
        result_msg = f"✅ {test_name}: Mensaje enviado"
        print(result_msg)
        return True, result_msg
    except Exception as e:
        message = f"❌ {test_name}: FAILED"
        if verbose:
            message += f" - {str(e)}"
        print(message)
        return False, message

def test_gelf_udp(config, verbose=False):
    """
    Envía mensaje de prueba vía GELF UDP.
    """
    test_name = "GELF UDP"
    try:
        host = config['host']
        port = config['ports']['gelf_udp']
        
        if verbose:
            print(f"  Enviando a {host}:{port}")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(config['timeout'])
        
        gelf_config = config['test_messages']['gelf']
        gelf_message = {
            "version": "1.1",
            "host": gelf_config['host'],
            "short_message": gelf_config['short_message'],
            "full_message": gelf_config['full_message'],
            "timestamp": datetime.now().timestamp(),
            "level": 6,
            "facility": "connectivity_test",
            "_test_type": "connectivity_check"
        }
        
        message = json.dumps(gelf_message).encode()
        sock.sendto(message, (host, port))
        sock.close()
        
        result_msg = f"✅ {test_name}: Mensaje enviado"
        print(result_msg)
        return True, result_msg
    except Exception as e:
        message = f"❌ {test_name}: FAILED"
        if verbose:
            message += f" - {str(e)}"
        print(message)
        return False, message

def run_connectivity_tests(config, verbose=False):
    """
    Ejecuta todas las pruebas de conectividad.
    """
    print(f"🔍 Probando Graylog en {config['host']}...")
    if verbose:
        print(f"Timeout configurado: {config['timeout']} segundos")
        print(f"Puertos: {config['ports']}")
    print("─" * 40)
    
    # Definir las pruebas a ejecutar
    tests = [
        ('Web Interface', test_web_interface),
        ('OpenSearch', test_opensearch),
        ('Syslog UDP', test_syslog_udp),
        ('GELF UDP', test_gelf_udp)
    ]
    
    results = []
    detailed_results = []
    
    for test_name, test_func in tests:
        if verbose:
            print(f"\n🔄 Ejecutando prueba: {test_name}")
        
        success, message = test_func(config, verbose)
        results.append(success)
        detailed_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    return results, detailed_results

def generate_report(config, results, detailed_results, output_file=None):
    """
    Genera un reporte de las pruebas ejecutadas.
    """
    print("─" * 40)
    
    passed = sum(results)
    total = len(results)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Mostrar resumen en consola
    if passed == total:
        print(f"🎉 TODAS LAS PRUEBAS PASARON ({passed}/{total})")
        print("✅ Graylog está funcionando correctamente")
        status = "SUCCESS"
    else:
        print(f"⚠️  ALGUNAS PRUEBAS FALLARON ({passed}/{total})")
        print("❌ Revisar configuración de Graylog")
        status = "PARTIAL_FAILURE"
    
    # Generar archivo de reporte si se solicita
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Reporte de Conectividad Graylog\n")
                f.write(f"# Generado el: {timestamp}\n")
                f.write(f"# Host probado: {config['host']}\n")
                f.write(f"# Estado general: {status}\n")
                f.write(f"# Pruebas exitosas: {passed}/{total}\n")
                f.write("=" * 60 + "\n\n")
                
                f.write("## Configuración utilizada:\n")
                f.write(f"- Host: {config['host']}\n")
                f.write(f"- Timeout: {config['timeout']} segundos\n")
                f.write("- Puertos:\n")
                for service, port in config['ports'].items():
                    f.write(f"  - {service}: {port}\n")
                f.write("\n")
                
                f.write("## Resultados detallados:\n")
                for result in detailed_results:
                    f.write(f"- {result['message']}\n")
                    f.write(f"  Timestamp: {result['timestamp']}\n\n")
            
            print(f"\n📄 Reporte guardado en: {output_file}")
        except Exception as e:
            print(f"⚠️  Error al guardar reporte: {e}")
    
    return status == "SUCCESS"

def main():
    """Función principal que ejecuta el programa."""
    try:
        # Parsear argumentos
        args = parse_arguments()
        
        # Cargar configuración
        config = load_config(args.config, args.host, args.timeout)
        
        # Ejecutar pruebas
        results, detailed_results = run_connectivity_tests(config, args.verbose)
        
        # Generar reporte
        success = generate_report(config, results, detailed_results, args.output)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pruebas interrumpidas por el usuario")
        return 130
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())

# Ejemplos de uso comentados:
# python graylog_checker.py
# python graylog_checker.py --host graylog.empresa.com
# python graylog_checker.py --config mi_graylog.yml --verbose
# python graylog_checker.py --host 192.168.1.100 --timeout 10 --output reporte.txt
# python graylog_checker.py --verbose --output reporte_detallado.txt