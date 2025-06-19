#!/usr/bin/env python3
"""
SVG Flattener
=============

Convierte un archivo SVG a un formato aplanado donde todos los elementos
básicos (rect, circle, ellipse, line, polyline, polygon) se convierten
en un único elemento <path>.

Uso:
    python svg_flattener.py input.svg output.svg
    python svg_flattener.py bot-to-flattenize.svg output/output.svg
"""

import argparse
import svgpathtools
from xml.etree import ElementTree as ET
from typing import Dict, Tuple, Optional, List


class SVGShapeConverter:
    """Convierte elementos SVG básicos a datos de path."""
    
    @staticmethod
    def rect_to_path(attrib: Dict[str, str]) -> str:
        """Convierte un rectángulo a path data."""
        x = float(attrib.get('x', 0))
        y = float(attrib.get('y', 0))
        width = float(attrib.get('width', 0))
        height = float(attrib.get('height', 0))
        rx = float(attrib.get('rx', 0))
        ry = float(attrib.get('ry', rx))

        if rx > 0 or ry > 0:
            rx = min(rx, width / 2)
            ry = min(ry, height / 2)
            return (
                f"M {x + rx} {y} "
                f"H {x + width - rx} "
                f"A {rx} {ry} 0 0 1 {x + width} {y + ry} "
                f"V {y + height - ry} "
                f"A {rx} {ry} 0 0 1 {x + width - rx} {y + height} "
                f"H {x + rx} "
                f"A {rx} {ry} 0 0 1 {x} {y + height - ry} "
                f"V {y + ry} "
                f"A {rx} {ry} 0 0 1 {x + rx} {y} Z"
            )
        else:
            return f"M {x} {y} H {x + width} V {y + height} H {x} Z"

    @staticmethod
    def circle_to_path(attrib: Dict[str, str]) -> str:
        """Convierte un círculo a path data."""
        cx = float(attrib.get('cx', 0))
        cy = float(attrib.get('cy', 0))
        r = float(attrib.get('r', 0))
        return (
            f"M {cx - r} {cy} "
            f"A {r} {r} 0 1 0 {cx + r} {cy} "
            f"A {r} {r} 0 1 0 {cx - r} {cy} Z"
        )

    @staticmethod
    def ellipse_to_path(attrib: Dict[str, str]) -> str:
        """Convierte una elipse a path data."""
        cx = float(attrib.get('cx', 0))
        cy = float(attrib.get('cy', 0))
        rx = float(attrib.get('rx', 0))
        ry = float(attrib.get('ry', 0))
        return (
            f"M {cx - rx} {cy} "
            f"A {rx} {ry} 0 1 0 {cx + rx} {cy} "
            f"A {rx} {ry} 0 1 0 {cx - rx} {cy} Z"
        )

    @staticmethod
    def line_to_path(attrib: Dict[str, str]) -> str:
        """Convierte una línea a path data."""
        x1 = float(attrib.get('x1', 0))
        y1 = float(attrib.get('y1', 0))
        x2 = float(attrib.get('x2', 0))
        y2 = float(attrib.get('y2', 0))
        return f"M {x1} {y1} L {x2} {y2}"

    @staticmethod
    def polyline_to_path(attrib: Dict[str, str]) -> str:
        """Convierte una polilínea a path data."""
        points_str = attrib.get('points', '')
        points = [tuple(map(float, p.split(','))) for p in points_str.strip().split()]
        
        if not points:
            return ""
            
        path_data = f"M {points[0][0]} {points[0][1]}"
        for p_x, p_y in points[1:]:
            path_data += f" L {p_x} {p_y}"
        return path_data

    @staticmethod
    def polygon_to_path(attrib: Dict[str, str]) -> str:
        """Convierte un polígono a path data."""
        points_str = attrib.get('points', '')
        points = [tuple(map(float, p.split(','))) for p in points_str.strip().split()]
        
        if not points:
            return ""
            
        path_data = f"M {points[0][0]} {points[0][1]}"
        for p_x, p_y in points[1:]:
            path_data += f" L {p_x} {p_y}"
        return path_data + " Z"

    @classmethod
    def convert_shape_to_path(cls, element, parent_attrib: Dict[str, str]) -> Tuple[Optional[str], Dict[str, str]]:
        """Convierte un elemento SVG a path data."""
        tag = element.tag.split('}')[-1]
        attrib = {**parent_attrib, **element.attrib}

        converters = {
            'rect': cls.rect_to_path,
            'circle': cls.circle_to_path,
            'ellipse': cls.ellipse_to_path,
            'line': cls.line_to_path,
            'polyline': cls.polyline_to_path,
            'polygon': cls.polygon_to_path,
        }

        if tag in converters:
            return converters[tag](attrib), attrib
        elif tag == 'path':
            return attrib.get('d', ''), attrib
        
        return None, attrib


class SVGFlattener:
    """Clase principal para aplanar archivos SVG."""
    
    DEFAULT_ATTRIBUTES = {
        'fill': 'none',
        'stroke': 'currentColor',
        'stroke-width': '2',
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
    }
    
    CONVERTIBLE_ELEMENTS = {'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path'}
    
    def __init__(self, input_file: str):
        """Inicializa el flattener con un archivo SVG."""
        self.input_file = input_file
        self.doc = None
        self.converter = SVGShapeConverter()
        
    def _load_svg(self) -> None:
        """Carga el archivo SVG."""
        try:
            self.doc = svgpathtools.Document(self.input_file)
        except Exception as e:
            raise ValueError(f"Error al cargar el archivo SVG: {e}")
    
    def _get_root_attributes(self) -> Dict[str, str]:
        """Obtiene los atributos del elemento raíz del SVG."""
        if self.doc.root is None:
            print("Warning: No se encontró elemento raíz, usando atributos por defecto")
            return self.DEFAULT_ATTRIBUTES.copy()
            
        print(f"Extrayendo atributos del elemento raíz...")
        attributes = {}
        for key, default_value in self.DEFAULT_ATTRIBUTES.items():
            attributes[key] = self.doc.root.get(key, default_value)
            
        # Agregar atributos adicionales si existen
        for attr in ['transform', 'style', 'opacity']:
            value = self.doc.root.get(attr)
            if value:
                attributes[attr] = value
                
        print(f"Atributos raíz extraídos: {list(attributes.keys())}")
        return attributes
    
    def _extract_path_data(self) -> List[str]:
        """Extrae todos los datos de path de los elementos convertibles."""
        print("Iniciando extracción de datos de path...")
        root_attributes = self._get_root_attributes()
        path_data_list = []
        element_count = 0
        
        for element in self.doc.tree.iter():
            tag = element.tag.split('}')[-1]
            
            if tag in self.CONVERTIBLE_ELEMENTS:
                element_count += 1
                print(f"Procesando elemento {element_count}: {tag}")
                path_data, _ = self.converter.convert_shape_to_path(element, root_attributes)
                if path_data:
                    path_data_list.append(path_data)
                    print(f"  ✓ Convertido a path data (longitud: {len(path_data)} caracteres)")
                else:
                    print(f"  ⚠ No se pudo convertir el elemento {tag}")
                    
        print(f"Extracción completada: {len(path_data_list)} elementos convertidos de {element_count} procesados")
        return path_data_list
    
    def _create_flattened_svg(self, combined_path_data: str) -> ET.Element:
        """Crea un nuevo elemento SVG con el path combinado."""
        print("Creando estructura SVG aplanada...")
        root = ET.Element('svg')
        
        if self.doc.root is not None:
            print("Copiando atributos del SVG original...")
            # Copiar atributos básicos del SVG
            basic_attrs = ['width', 'height', 'viewBox', 'xmlns']
            defaults = {
                'width': '100%',
                'height': '100%',
                'viewBox': '0 0 24 24',
                'xmlns': 'http://www.w3.org/2000/svg'
            }
            
            for attr in basic_attrs:
                value = self.doc.root.get(attr, defaults.get(attr))
                if value:
                    root.set(attr, value)
            
            # Copiar otros atributos relevantes
            style_attrs = {'fill', 'stroke', 'stroke-width', 'stroke-linecap', 
                          'stroke-linejoin', 'transform', 'style', 'opacity'}
            
            additional_attrs = 0
            for attr, value in self.doc.root.attrib.items():
                if attr not in basic_attrs and attr not in style_attrs:
                    root.set(attr, value)
                    additional_attrs += 1
            
            print(f"Atributos copiados: {len(basic_attrs)} básicos, {additional_attrs} adicionales")
        else:
            print("Warning: No se encontró elemento raíz, usando configuración por defecto")
        
        # Crear el elemento path combinado
        if combined_path_data:
            print(f"Creando path combinado (longitud: {len(combined_path_data)} caracteres)...")
            path_element = ET.SubElement(root, 'path')
            path_element.set('d', combined_path_data)
            
            # Aplicar atributos de estilo
            root_attributes = self._get_root_attributes()
            style_count = 0
            for key, value in root_attributes.items():
                path_element.set(key, value)
                style_count += 1
            print(f"Aplicados {style_count} atributos de estilo al path")
        else:
            print("Warning: No hay datos de path para combinar")
        
        print("Estructura SVG aplanada creada exitosamente")
        return root
    
    def flatten_to_file(self, output_file: str) -> None:
        """Aplana el SVG y lo guarda en un archivo."""
        print(f"Iniciando procesamiento del archivo: {self.input_file}")
        self._load_svg()
        print(f"✓ Archivo SVG cargado exitosamente")
        
        path_data_list = self._extract_path_data()
        combined_path_data = " ".join(path_data_list)
        print(f"Path data combinado: {len(combined_path_data)} caracteres totales")
        
        flattened_root = self._create_flattened_svg(combined_path_data)
        
        try:
            print(f"Guardando archivo aplanado en: {output_file}")
            tree = ET.ElementTree(flattened_root)
            ET.indent(tree, space="  ", level=0)
            tree.write(output_file, encoding='utf-8', xml_declaration=True)
            print(f"✓ SVG aplanado guardado exitosamente en: {output_file}")
        except Exception as e:
            raise IOError(f"Error al guardar el archivo SVG: {e}")


def parse_arguments() -> argparse.Namespace:
    """Parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Convierte un archivo SVG a un formato aplanado donde todos los elementos "
                   "básicos se convierten en un único elemento <path>.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("input_file", help="Archivo SVG de entrada")
    parser.add_argument("output_file", help="Archivo SVG de salida")
    return parser.parse_args()


def main() -> int:
    """Función principal."""
    try:
        print("=== SVG Flattener v2.0.0 ===")
        args = parse_arguments()
        print(f"Archivo de entrada: {args.input_file}")
        print(f"Archivo de salida: {args.output_file}")
        print("-" * 40)
        
        flattener = SVGFlattener(args.input_file)
        flattener.flatten_to_file(args.output_file)
        
        print("-" * 40)
        print("✓ Proceso completado exitosamente")
        return 0
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
    
# Ejemplos de uso comentados:
# python svg_flatten.py bot-to-flattenize.svg output/flatten-bot.svg    