#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# SCRIPT DE BACKUP PARALELO CON RSYNC
# ═══════════════════════════════════════════════════════════════

# ────────────────────────────────────────────────────────────────
# 1. INSTALACIÓN DE DEPENDENCIAS
# ────────────────────────────────────────────────────────────────
# Instalar GNU Parallel (solo la primera vez):
#   brew install parallel

# ────────────────────────────────────────────────────────────────
# 2. DAR PERMISOS DE EJECUCIÓN
# ────────────────────────────────────────────────────────────────
# chmod +x ~/backup-app/copy-backup-parallel.sh

# ────────────────────────────────────────────────────────────────
# 3. EJECUCIÓN NORMAL
# ────────────────────────────────────────────────────────────────
# cd ~/backup-app
# ./copy-backup-parallel.sh

# ────────────────────────────────────────────────────────────────
# 4. EJECUCIÓN CON CAFFEINATE (RECOMENDADO)
# ────────────────────────────────────────────────────────────────
# Para evitar que tu Mac se duerma durante el backup:
#   caffeinate -disu ./copy-backup-parallel.sh
#
# Flags de caffeinate:
#   -d = Previene que el display se apague
#   -i = Previene que el sistema idle sleep se active
#   -s = Previene que el sistema se duerma si está conectado a AC
#   -u = Declara que la actividad del usuario está ocurriendo

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════

SOURCE="/Volumes/BOOTCAMP/windows11bkp/fotos"
DEST="/Volumes/BACKUP/fotos"
LOG_FILE="$HOME/Desktop/copy_progress.log"
COMPLETED_FILE="$HOME/Desktop/completed_folders.txt"
TEMP_DIR="$HOME/Desktop/copy_temp"

# Número de carpetas a copiar en paralelo
# Ajusta según tu hardware:
#   - SSD: 4-6 trabajos
#   - HDD externo: 2-3 trabajos
#   - Disco de red: 2-3 trabajos
MAX_JOBS=4

# ═══════════════════════════════════════════════════════════════
# VERIFICACIÓN DE DEPENDENCIAS
# ═══════════════════════════════════════════════════════════════

if ! command -v parallel &> /dev/null; then
    echo "❌ ERROR: GNU Parallel no está instalado"
    echo ""
    echo "Por favor instálalo con:"
    echo "  brew install parallel"
    echo ""
    exit 1
fi

# ═══════════════════════════════════════════════════════════════
# FUNCIONES
# ═══════════════════════════════════════════════════════════════

# Función para copiar una carpeta (se ejecutará en paralelo)
copy_folder() {
    local folder="$1"
    local folder_name=$(basename "$folder")
    local job_log="$TEMP_DIR/${folder_name}.log"
    
    # Verificar si ya fue copiada anteriormente
    if grep -Fxq "$folder_name" "$COMPLETED_FILE" 2>/dev/null; then
        echo "⏭️  OMITIDA: $folder_name (ya copiada anteriormente) [$(date +%H:%M:%S)]" >> "$job_log"
        return 0
    fi
    
    echo "📁 Iniciando: $folder_name [$(date +%H:%M:%S)]" >> "$job_log"
    
    # Copiar con rsync mostrando progreso
    if rsync -a --info=progress2 "$folder" "$DEST/" >> "$job_log" 2>&1; then
        # Marcar como completada (con lock para evitar condiciones de carrera)
        (
            flock -x 200
            echo "$folder_name" >> "$COMPLETED_FILE"
        ) 200>"$COMPLETED_FILE.lock"
        
        echo "✅ COMPLETADO: $folder_name [$(date +%H:%M:%S)]" >> "$job_log"
        return 0
    else
        echo "❌ ERROR: $folder_name [$(date +%H:%M:%S)]" >> "$job_log"
        return 1
    fi
}

# Exportar la función para que GNU Parallel pueda usarla
export -f copy_folder
export COMPLETED_FILE DEST TEMP_DIR

# ═══════════════════════════════════════════════════════════════
# PREPARACIÓN
# ═══════════════════════════════════════════════════════════════

# Crear directorios y archivos necesarios
mkdir -p "$TEMP_DIR"
mkdir -p "$DEST"
touch "$COMPLETED_FILE"
touch "$COMPLETED_FILE.lock"

# Limpiar log anterior si existe
> "$LOG_FILE"

# ═══════════════════════════════════════════════════════════════
# INICIO DEL BACKUP
# ═══════════════════════════════════════════════════════════════

echo "╔════════════════════════════════════════════════════════╗"
echo "║         BACKUP PARALELO - INICIANDO                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo "" | tee -a "$LOG_FILE"
echo "📅 Fecha: $(date)" | tee -a "$LOG_FILE"
echo "📁 Origen: $SOURCE" | tee -a "$LOG_FILE"
echo "💾 Destino: $DEST" | tee -a "$LOG_FILE"
echo "🔄 Jobs paralelos: $MAX_JOBS" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Contar total de carpetas a procesar
total=$(find "$SOURCE" -maxdepth 1 -type d ! -path "$SOURCE" | wc -l | tr -d ' ')
echo "📊 Total de carpetas a procesar: $total" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Verificar que hay carpetas para procesar
if [ "$total" -eq 0 ]; then
    echo "⚠️  No se encontraron carpetas en: $SOURCE"
    exit 0
fi

echo "⏳ Procesando carpetas en paralelo..." | tee -a "$LOG_FILE"
echo "   (Puedes ver el progreso en tiempo real abajo)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# ═══════════════════════════════════════════════════════════════
# EJECUCIÓN PARALELA
# ═══════════════════════════════════════════════════════════════

# Ejecutar copias en paralelo con barra de progreso
# --bar: Muestra barra de progreso
# --jobs: Número de trabajos en paralelo
# --eta: Muestra tiempo estimado de finalización
find "$SOURCE" -maxdepth 1 -type d ! -path "$SOURCE" | \
    parallel --bar --jobs "$MAX_JOBS" --eta copy_folder {}

# ═══════════════════════════════════════════════════════════════
# CONSOLIDACIÓN DE RESULTADOS
# ═══════════════════════════════════════════════════════════════

echo "" | tee -a "$LOG_FILE"
echo "📝 Consolidando logs..." | tee -a "$LOG_FILE"

# Consolidar todos los logs individuales en el log principal
for log in "$TEMP_DIR"/*.log; do
    if [ -f "$log" ]; then
        cat "$log" >> "$LOG_FILE"
    fi
done

# ═══════════════════════════════════════════════════════════════
# CÁLCULO DE ESTADÍSTICAS
# ═══════════════════════════════════════════════════════════════

copied=$(grep -c "✅ COMPLETADO" "$LOG_FILE" 2>/dev/null || echo "0")
skipped=$(grep -c "⏭️  OMITIDA" "$LOG_FILE" 2>/dev/null || echo "0")
errors=$(grep -c "❌ ERROR" "$LOG_FILE" 2>/dev/null || echo "0")

# ═══════════════════════════════════════════════════════════════
# RESUMEN FINAL
# ═══════════════════════════════════════════════════════════════

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║               RESUMEN FINAL                            ║"
echo "╚════════════════════════════════════════════════════════╝"
echo "📊 Total de carpetas: $total" | tee -a "$LOG_FILE"
echo "✅ Copiadas exitosamente: $copied" | tee -a "$LOG_FILE"
echo "⏭️  Omitidas (ya existían): $skipped" | tee -a "$LOG_FILE"
echo "❌ Errores: $errors" | tee -a "$LOG_FILE"
echo "🕐 Finalizado: $(date)" | tee -a "$LOG_FILE"
echo ""
echo "📄 Log detallado guardado en: $LOG_FILE"
echo ""

# ═══════════════════════════════════════════════════════════════
# LIMPIEZA
# ═══════════════════════════════════════════════════════════════

rm -rf "$TEMP_DIR"
rm -f "$COMPLETED_FILE.lock"

# ═══════════════════════════════════════════════════════════════
# NOTIFICACIÓN FINAL
# ═══════════════════════════════════════════════════════════════

if [ "$errors" -eq 0 ]; then
    echo "✅ Backup completado exitosamente"
    # Notificación del sistema (opcional)
    osascript -e 'display notification "Todas las carpetas fueron respaldadas correctamente" with title "✅ Backup Completado" sound name "Glass"' 2>/dev/null
else
    echo "⚠️  Backup completado con $errors errores"
    echo "   Revisa el archivo de log para más detalles"
    osascript -e 'display notification "El backup finalizó pero hubo algunos errores" with title "⚠️ Backup con Errores" sound name "Basso"' 2>/dev/null
fi

echo ""
echo "═══════════════════════════════════════════════════════════"