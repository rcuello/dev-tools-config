#!/bin/bash

# Configuración
SOURCE="/Volumes/BOOTCAMP/windows11bkp/DevOps"
LOG_FILE="$HOME/Desktop/delete_progress.log"
THREADS=4  # Ajusta según los núcleos de tu Mac

echo "=== Eliminación paralela de node_modules y .git ===" | tee -a "$LOG_FILE"
echo "Fecha: $(date)" | tee -a "$LOG_FILE"
echo "Hilos paralelos: $THREADS" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "🔍 Buscando y eliminando carpetas..." | tee -a "$LOG_FILE"

# Eliminar en paralelo
find "$SOURCE" -type d \( -name "node_modules" -o -name ".git" \) -print0 | \
    xargs -0 -P $THREADS -I {} sh -c 'echo "🗑️  Eliminando: {}" && rm -rf "{}" && echo "   ✅ Eliminado: {}"' 2>&1 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "✅ Eliminación completada: $(date)" | tee -a "$LOG_FILE"
echo "💾 Espacio en disco:" | tee -a "$LOG_FILE"
df -h "$SOURCE" | tee -a "$LOG_FILE"