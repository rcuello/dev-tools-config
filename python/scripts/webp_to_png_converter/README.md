# WebpToPngConverter

Script para convertir imágenes en formato `.webp` a `.png`, ya sea de forma individual o por lotes desde un directorio.

## 📦 Requisitos

Instala las dependencias con:

```bash
pip install -r requirements.txt
````

Este proyecto utiliza [Pillow](https://pillow.readthedocs.io/) para la conversión de imágenes.

---

## 🚀 Uso

```bash
python webp_converter_main.py [opciones]
```

### 🎯 Opciones

* `-f`, `--file`: Ruta al archivo `.webp` a convertir.
* `-d`, `--directory`: Directorio que contiene archivos `.webp` a convertir.
* `-o`, `--output`: Ruta de salida para los archivos `.png` (archivo o directorio).
* `-v`, `--verbose`: Muestra información detallada de los archivos convertidos.

⚠️ Se debe especificar **una y solo una** de las opciones `--file` o `--directory`.

---

## 🔍 Ejemplos

### ✅ Convertir un solo archivo

```bash
python webp_converter_main.py -f imagen.webp
```

### ✅ Convertir un archivo y especificar la salida

```bash
python webp_converter_main.py -f imagen.webp -o salida/imagen_convertida.png
```

### ✅ Convertir todos los archivos `.webp` en un directorio

```bash
python webp_converter_main.py -d carpeta_con_webps
```

### ✅ Convertir archivos en un directorio y especificar el destino

```bash
python webp_converter_main.py -d carpeta_con_webps -o carpeta_de_salida
```

### ✅ Convertir con salida detallada (verbose)

```bash
python webp_converter_main.py -d carpeta_con_webps -v
```

---

## 🧪 Recomendación

Asegúrate de que los archivos `.webp` sean válidos y que la carpeta de salida tenga permisos de escritura.


---

### ✅ Siguientes pasos

1. Guarda tu script `webp_converter_main.py` en la raíz del proyecto.
2. Asegúrate de tener el archivo `webp_to_png_converter.py` implementado.
3. Ejecuta `pip install -r requirements.txt` para preparar el entorno.
4. ¡Listo para convertir imágenes!
