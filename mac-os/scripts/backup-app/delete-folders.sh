#!/bin/bash

# Configuración
SOURCE="/Volumes/BOOTCAMP/windows11bkp"
LOG_FILE="$HOME/Desktop/delete_progress.log"

echo "=== Iniciando eliminación de node_modules y .git ===" | tee -a "$LOG_FILE"
echo "Fecha: $(date)" | tee -a "$LOG_FILE"
echo "Carpeta: $SOURCE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Contadores
total_node_modules=0
total_git=0
deleted_node_modules=0
deleted_git=0
errors=0

# Contar carpetas a eliminar
echo "🔍 Buscando carpetas node_modules..." | tee -a "$LOG_FILE"
while IFS= read -r -d '' folder; do
    ((total_node_modules++))
done < <(find "$SOURCE" -type d -name "node_modules" -print0)

echo "🔍 Buscando carpetas .git..." | tee -a "$LOG_FILE"
while IFS= read -r -d '' folder; do
    ((total_git++))
done < <(find "$SOURCE" -type d -name ".git" -print0)

echo "" | tee -a "$LOG_FILE"
echo "📊 Encontradas:" | tee -a "$LOG_FILE"
echo "   - node_modules: $total_node_modules" | tee -a "$LOG_FILE"
echo "   - .git: $total_git" | tee -a "$LOG_FILE"
echo "   - TOTAL: $((total_node_modules + total_git))" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

read -p "¿Deseas continuar con la eliminación? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    echo "❌ Operación cancelada" | tee -a "$LOG_FILE"
    exit 1
fi

echo "" | tee -a "$LOG_FILE"
echo "🗑️  Eliminando carpetas node_modules..." | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Eliminar node_modules
while IFS= read -r -d '' folder; do
    ((deleted_node_modules++))
    echo "[$deleted_node_modules/$total_node_modules] Eliminando: $folder" | tee -a "$LOG_FILE"
    
    if rm -rf "$folder" 2>&1 | tee -a "$LOG_FILE"; then
        echo "   ✅ Eliminado" | tee -a "$LOG_FILE"
    else
        echo "   ❌ Error al eliminar" | tee -a "$LOG_FILE"
        ((errors++))
    fi
done < <(find "$SOURCE" -type d -name "node_modules" -print0)

echo "" | tee -a "$LOG_FILE"
echo "🗑️  Eliminando carpetas .git..." | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Eliminar .git
while IFS= read -r -d '' folder; do
    ((deleted_git++))
    echo "[$deleted_git/$total_git] Eliminando: $folder" | tee -a "$LOG_FILE"
    
    if rm -rf "$folder" 2>&1 | tee -a "$LOG_FILE"; then
        echo "   ✅ Eliminado" | tee -a "$LOG_FILE"
    else
        echo "   ❌ Error al eliminar" | tee -a "$LOG_FILE"
        ((errors++))
    fi
done < <(find "$SOURCE" -type d -name ".git" -print0)

# Resumen final
echo "" | tee -a "$LOG_FILE"
echo "=== RESUMEN ===" | tee -a "$LOG_FILE"
echo "node_modules eliminadas: $deleted_node_modules/$total_node_modules" | tee -a "$LOG_FILE"
echo ".git eliminadas: $deleted_git/$total_git" | tee -a "$LOG_FILE"
echo "Errores: $errors" | tee -a "$LOG_FILE"
echo "Finalizado: $(date)" | tee -a "$LOG_FILE"

# Mostrar espacio liberado
echo "" | tee -a "$LOG_FILE"
echo "💾 Verificando espacio en disco..." | tee -a "$LOG_FILE"
df -h "$SOURCE" | tee -a "$LOG_FILE"