# 🔧 Restablecer la Contraseña en WSL (Ubuntu)

Si olvidaste la contraseña de tu usuario en WSL (Windows Subsystem for Linux), puedes restablecerla sin necesidad de reinstalar la distribución. Sigue estos pasos:

## 📌 Método 1: Cambiar la Contraseña sin Reinstalar

1. **Abrir PowerShell como Administrador**  
   - Presiona `Win + X` y selecciona **PowerShell (Administrador)** o **Terminal (Administrador)**.

2. **Listar las distribuciones instaladas**  
   Ejecuta el siguiente comando para ver el nombre de tu distribución de Ubuntu en WSL:  
   ```powershell
   wsl -l -v
   ```
   Busca el nombre exacto de la distribución (por ejemplo, `Ubuntu-22.04`).

3. **Iniciar WSL como `root`**  
   Ejecuta este comando en PowerShell:  
   ```powershell
   wsl -u root
   ```
   Esto abrirá WSL como usuario `root`, que no necesita contraseña.

4. **Cambiar la contraseña del usuario**  
   Dentro de WSL, usa el siguiente comando para restablecer la contraseña de tu usuario:  
   ```bash
   passwd TU_USUARIO
   ```
   Reemplaza `TU_USUARIO` con el nombre de tu usuario en WSL y sigue las instrucciones para establecer una nueva contraseña.

5. **Cerrar sesión y probar el acceso**  
   - Sal de WSL con `exit`.  
   - Vuelve a abrir WSL normalmente e ingresa la nueva contraseña cuando se solicite.

---

## 📌 Método 2: Reinstalar Ubuntu en WSL  
Si prefieres hacer una reinstalación desde cero, sigue estos pasos:

1. **Eliminar la distribución de WSL**  
   - Abre `Configuración` > `Aplicaciones` > `Aplicaciones instaladas`.
   - Busca `Ubuntu`, selecciona `Desinstalar`.

2. **Reinstalar Ubuntu**  
   - Ve a la **Microsoft Store** y descarga nuevamente `Ubuntu`.

Esto eliminará todos los archivos y configuraciones anteriores, iniciando con una instalación limpia.
