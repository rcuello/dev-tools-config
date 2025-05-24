from PIL import Image
import os
import logging

class WebpToPngConverter:
    """
    Clase simple para convertir archivos WEBP a formato PNG.
    Utiliza la biblioteca Pillow (PIL) para las operaciones de imagen.
    """
    
    def __init__(self, input_path=None, output_path=None):
        """
        Inicializa el conversor con rutas de entrada y salida opcionales.
        
        Args:
            input_path (str, optional): Ruta del archivo WEBP de entrada.
            output_path (str, optional): Ruta donde guardar el archivo PNG convertido.
        """
        self.input_path = input_path
        self.output_path = output_path
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura el sistema de logging básico."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('WebpToPngConverter')
    
    def convert(self, input_path=None, output_path=None):
        """
        Convierte un archivo WEBP a PNG.
        
        Args:
            input_path (str, optional): Ruta del archivo WEBP a convertir.
                Si no se proporciona, se usa self.input_path.
            output_path (str, optional): Ruta donde guardar el archivo PNG.
                Si no se proporciona, se usa self.output_path o se genera automáticamente.
                
        Returns:
            str: Ruta del archivo PNG generado.
            
        Raises:
            ValueError: Si no se proporciona una ruta de entrada válida.
            FileNotFoundError: Si el archivo de entrada no existe.
            Exception: Para otros errores durante la conversión.
        """
        # Usar los parámetros proporcionados o los valores predeterminados
        input_path = input_path or self.input_path
        
        # Validar la ruta de entrada
        if not input_path:
            raise ValueError("Se requiere una ruta de archivo de entrada")
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"El archivo {input_path} no existe")
        
        # Generar la ruta de salida si no se proporciona
        if not output_path and not self.output_path:
            # Cambiar la extensión de .webp a .png
            output_path = os.path.splitext(input_path)[0] + '.png'
        else:
            output_path = output_path or self.output_path
        
        try:
            # Abrir y convertir la imagen
            self.logger.info(f"Convirtiendo {input_path} a PNG")
            with Image.open(input_path) as img:
                # Guardar como PNG
                img.save(output_path, 'PNG')
            
            self.logger.info(f"Conversión completada. Archivo guardado en {output_path}")
            return output_path
        
        except Exception as e:
            self.logger.error(f"Error durante la conversión: {str(e)}")
            raise
    
    def convert_directory(self, input_dir, output_dir=None):
        """
        Convierte todos los archivos WEBP en un directorio a PNG.
        
        Args:
            input_dir (str): Directorio con archivos WEBP.
            output_dir (str, optional): Directorio donde guardar los archivos PNG.
                Si no se proporciona, se guardan en el mismo directorio.
                
        Returns:
            list: Lista de rutas de los archivos PNG generados.
        """
        if not os.path.isdir(input_dir):
            raise NotADirectoryError(f"{input_dir} no es un directorio válido")
        
        # Si no se proporciona un directorio de salida, usar el mismo directorio
        if not output_dir:
            output_dir = input_dir
        elif not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        converted_files = []
        
        # Iterar sobre todos los archivos en el directorio
        for filename in os.listdir(input_dir):
            if filename.lower().endswith('.webp'):
                input_path = os.path.join(input_dir, filename)
                output_filename = os.path.splitext(filename)[0] + '.png'
                output_path = os.path.join(output_dir, output_filename)
                
                try:
                    self.convert(input_path, output_path)
                    converted_files.append(output_path)
                except Exception as e:
                    self.logger.error(f"Error al convertir {filename}: {str(e)}")
        
        self.logger.info(f"Conversión de directorio completada. {len(converted_files)} archivos convertidos.")
        return converted_files