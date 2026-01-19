#!/bin/bash

# Configuración
SOURCE="/Volumes/BOOTCAMP/windows11bkp/DevOps"
REPORT_FILE="$HOME/Desktop/problematic_folders.txt"

echo "=== Análisis de carpetas problemáticas ===" | tee "$REPORT_FILE"
echo "Fecha: $(date)" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

echo "🔍 Buscando carpetas node_modules y .git..." | tee -a "$REPORT_FILE"
echo "📂 Carpeta origen: $SOURCE" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

accessible=0
no_read=0
no_access=0
slow=0
total=0
last_parent=""

# Función para verificar carpeta con timeout manual
check_folder_with_timeout() {
    local folder="$1"
    local timeout_duration=3
    
    # Ejecutar ls en background
    ls "$folder" >/dev/null 2>&1 &
    local pid=$!
    
    # Esperar con timeout
    local count=0
    while kill -0 $pid 2>/dev/null; do
        if [ $count -ge $timeout_duration ]; then
            kill -9 $pid 2>/dev/null
            wait $pid 2>/dev/null
            return 1  # Timeout
        fi
        sleep 0.5
        ((count++))
    done
    
    wait $pid
    return $?
}

echo "Iniciando escaneo..."
echo ""

while IFS= read -r -d '' folder; do
    ((total++))
    
    # Obtener directorio padre
    current_parent=$(dirname "$folder")
    
    # Mostrar cambio de directorio
    if [ "$current_parent" != "$last_parent" ]; then
        echo ""
        echo "📁 $current_parent"
        last_parent="$current_parent"
    fi
    
    folder_name=$(basename "$folder")
    printf "   [%4d] 🔎 %-30s" "$total" "$folder_name"
    
    # Verificar permisos básicos
    if [ ! -r "$folder" ]; then
        echo " 🔒 SIN PERMISOS" | tee -a "$REPORT_FILE"
        ((no_read++))
        continue
    fi
    
    # Verificar acceso con timeout
    start=$(date +%s)
    if check_folder_with_timeout "$folder"; then
        end=$(date +%s)
        elapsed=$((end - start))
        
        if [ $elapsed -gt 2 ]; then
            echo " ⚠️  LENTO (${elapsed}s)" | tee -a "$REPORT_FILE"
            ((slow++))
        else
            echo " ✅"
        fi
        ((accessible++))
    else
        echo " ❌ TIMEOUT/ERROR" | tee -a "$REPORT_FILE"
        ((no_access++))
    fi
    
done < <(find "$SOURCE" -type d \( -name "node_modules" -o -name ".git" \) -print0 2>/dev/null)

echo ""
echo ""
echo "=== RESUMEN ===" | tee -a "$REPORT_FILE"
echo "Total encontradas: $total" | tee -a "$REPORT_FILE"
echo "✅ Accesibles: $accessible" | tee -a "$REPORT_FILE"
echo "⚠️  Lentas (>2s): $slow" | tee -a "$REPORT_FILE"
echo "🔒 Sin permisos: $no_read" | tee -a "$REPORT_FILE"
echo "❌ Timeout/Error: $no_access" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

if [ $total -gt 0 ]; then
    problematic=$((no_read + no_access))
    percentage=$((problematic * 100 / total))
    echo "Problemáticas: $problematic ($percentage%)" | tee -a "$REPORT_FILE"
fi

echo "" | tee -a "$REPORT_FILE"
echo "Finalizado: $(date)" | tee -a "$REPORT_FILE"