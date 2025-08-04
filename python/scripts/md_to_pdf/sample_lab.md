# 🧪 Laboratorio: Introducción a la Terminal y Programación Java sin IDE

**Asignatura:** Fundamentos de Programación  
**Semestre:** II  
**Duración Estimada:** 2 horas  
**Objetivo General:**  
Familiarizar al estudiante con el uso de la consola de comandos (CMD/PowerShell) en Windows para crear, compilar y ejecutar un programa Java sin depender de un entorno de desarrollo integrado (IDE).

---

## ✅ Resultados de Aprendizaje

Al finalizar este laboratorio, el estudiante será capaz de:

- Navegar por el sistema de archivos desde la terminal.  
- Crear y gestionar carpetas de trabajo mediante comandos.  
- Escribir código fuente Java utilizando un editor de texto plano.  
- Compilar código fuente usando `javac` y ejecutar aplicaciones Java con `java`.  
- Interpretar errores comunes de compilación y aplicar correcciones.

---

## 🧰 Requisitos Previos

Antes de iniciar, asegúrate de cumplir con lo siguiente:

| Requisito | Detalles |
|-----------|----------|
| Sistema Operativo | Windows 10 o superior |
| Java Development Kit (JDK) | JDK 11 o superior instalado y configurado |
| Variable de entorno `PATH` | Verificable con `java -version` y `javac -version` desde la terminal |
| Editor de texto | Notepad++, Visual Studio Code, o Bloc de Notas (sin autocompletado obligatorio) |


---

## 🧭 Sección: Explorando la Terminal (20 minutos)

### Objetivo  
Aprender comandos básicos para manipular archivos y directorios.

### Instrucciones

Abrir la terminal:  
Presiona `Win + R`, escribe `cmd` o `powershell` y presiona Enter.

Consultar la ubicación actual: 
 
```bash
cd
```

Listar los archivos del directorio actual:

```bash
dir
```

Ir a la carpeta de Documentos:

```bash
cd %USERPROFILE%\Documents
```

Crear una carpeta para el laboratorio y acceder a ella:

```bash
mkdir LaboratorioTerminalJava
cd LaboratorioTerminalJava
```

Verificar la carpeta actual:

```bash
cd
```

Tips adicionales:

* `cls`: limpia la terminal.
* `cd ..`: sube al directorio anterior.
* Usa `Tab` para autocompletar nombres de carpetas.

---

## 💻 Sección: Escribir y Compilar tu Primer Programa (30 minutos)

### Objetivo

Crear, compilar y entender el flujo de trabajo básico de Java desde consola.

### Código fuente

Crea un nuevo archivo llamado `MiPrimerPrograma.java` con el siguiente contenido:

```java
public class MiPrimerPrograma {
    public static void main(String[] args) {
        System.out.println("¡Hola desde la terminal de Windows!");
    }
}
```

Guárdalo en la carpeta `LaboratorioTerminalJava`.

### Compilación

Desde la terminal, ejecuta:

```bash
javac MiPrimerPrograma.java
```

Verifica con `dir` que se haya generado el archivo `MiPrimerPrograma.class`.

### Análisis

Incluye en tu informe las respuestas a las siguientes preguntas:

* ¿Qué hizo el comando `javac`?
* ¿Cuál es la diferencia entre los archivos `.java` y `.class`?

---

## 🧪 Sección: Ejecutar el Programa y Simular un Error (30 minutos)

### Objetivo

Ejecutar el código compilado, inducir errores y aprender a leer mensajes del compilador.

### Ejecución

Desde la terminal, ejecuta:

```bash
java MiPrimerPrograma
```

Deberías ver el mensaje:

```
¡Hola desde la terminal de Windows!
```

### Simulación de error

Edita `MiPrimerPrograma.java` y **elimina el punto y coma** al final de la línea `System.out.println(...)`. Guarda el archivo.

Vuelve a compilar:

```bash
javac MiPrimerPrograma.java
```

Captura el mensaje de error completo mostrado por el compilador.

### Diagnóstico

Incluye en tu informe:

* ¿Qué error mostró el compilador?
* ¿Qué línea lo causó?
* ¿Cómo lo resolviste?

---

## 🗂️ Sección: Reflexión Técnica (10 minutos)

Redacta brevemente en tu informe las siguientes reflexiones:

* ¿Qué ventajas tiene entender y usar la terminal en vez de un IDE?
* ¿Qué aprendiste sobre la estructura y ejecución de programas en Java?
* ¿Qué errores cometiste y cómo los solucionaste?

---

## 📦 Entregables

Debes subir un archivo `.zip` con la siguiente estructura:

```
LaboratorioTerminalJava/
├── MiPrimerPrograma.java
├── Capturas/
│   ├── paso1_creacion_carpeta.png
│   ├── paso2_compilacion_exitosa.png
│   ├── paso3_ejecucion.png
│   ├── paso4_error_compilacion.png
└── Informe.pdf (o .docx)
```

### Contenido del Informe

Incluye:

* Explicación del comando `javac`.
* Comparación entre `.java` y `.class`.
* Captura y análisis del mensaje de error del compilador.
* Explicación del proceso de corrección.
* Reflexión personal sobre el uso de la terminal.

---



