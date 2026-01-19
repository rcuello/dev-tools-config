#!/bin/bash

# Configuración
SOURCE="/Volumes/BOOTCAMP/windows11bkp/fotos"
DEST="/Volumes/BACKUP/fotos"
LOG_FILE="$HOME/Desktop/copy_progress.log"
COMPLETED_FILE="$HOME/Desktop/completed_folders.txt"

# Crear archivo de carpetas completadas si no existe
touch "$COMPLETED_FILE"

# Función para verificar si una carpeta ya fue copiada
is_completed() {
    grep -Fxq "$1" "$COMPLETED_FILE"
}

# Función para marcar carpeta como completada
mark_completed() {
    echo "$1" >> "$COMPLETED_FILE"
}

# Crear destino si no existe
mkdir -p "$DEST"

echo "=== Iniciando copia incremental ===" | tee -a "$LOG_FILE"
echo "Fecha: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Contador
total=0
skipped=0
copied=0
errors=0

# Contar total de carpetas
for folder in "$SOURCE"/*; do
    if [ -d "$folder" ]; then
        ((total++))
    fi
done

echo "Total de carpetas a procesar: $total" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Procesar cada carpeta
for folder in "$SOURCE"/*; do
    if [ -d "$folder" ]; then
        folder_name=$(basename "$folder")
        
        # Verificar si ya fue copiada
        if is_completed "$folder_name"; then
            echo "⏭️  OMITIDA: $folder_name (ya copiada anteriormente)" | tee -a "$LOG_FILE"
            ((skipped++))
            continue
        fi
        
        echo "📁 Copiando: $folder_name" | tee -a "$LOG_FILE"
        echo "   Progreso: $((copied + skipped + 1))/$total" | tee -a "$LOG_FILE"
        
        # Copiar con rsync (maneja errores mejor que cp)
        if rsync -a --progress "$folder" "$DEST/" 2>&1 | tee -a "$LOG_FILE"; then
            mark_completed "$folder_name"
            echo "✅ COMPLETADO: $folder_name" | tee -a "$LOG_FILE"
            ((copied++))
        else
            echo "❌ ERROR al copiar: $folder_name" | tee -a "$LOG_FILE"
            ((errors++))
        fi
        
        echo "" | tee -a "$LOG_FILE"
    fi
done

# Resumen final
echo "=== RESUMEN ===" | tee -a "$LOG_FILE"
echo "Total: $total carpetas" | tee -a "$LOG_FILE"
echo "Copiadas: $copied" | tee -a "$LOG_FILE"
echo "Omitidas: $skipped" | tee -a "$LOG_FILE"
echo "Errores: $errors" | tee -a "$LOG_FILE"
echo "Finalizado: $(date)" | tee -a "$LOG_FILE"