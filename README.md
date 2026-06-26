# Cuentas Claras 🎯💰 - Erradicando la Amnesia Financiera Estudiantil

**Cuentas Claras** es una plataforma web desarrollada en **Django** diseñada para llevar un control divertido, transparente y sumamente visual de las deudas pequeñas entre compañeros de clase (como esa malta, empanada o fotocopia que prometieron pagarte "al salir de clases"). 

Inspirada en una estética **Cyber-Neon / Fanvue**, la interfaz ofrece un diseño premium en modo oscuro con acentos magenta y ciano, bordes translúcidos y animaciones fluidas.

---

## ✨ Características Principales

*   📁 **El Tablón de los Buscados**: Un dashboard público responsivo en formato de tarjetas de cristal (glassmorphism) donde cualquier visitante puede ver las deudas pendientes de la comunidad.
*   📸 **Evidencias Físicas**: Capacidad de adjuntar capturas, fotos del sospechoso comiendo la malta o memes graciosos como prueba irrefutable de la deuda.
*   🔒 **Seguridad y "Regla de Oro"**: 
    *   Cualquiera puede ver las deudas, pero **sólo el acreedor original (dueño)** que registró la deuda tiene la potestad de modificarla o marcarla como pagada (borrarla).
    *   Cualquier intento de sabotaje por parte de terceros o deudores a través de peticiones HTTP forzadas es bloqueado con un error estricto de servidor **403 Forbidden**.
*   🚨 **Reporte de Sospechosos**: Sección satírica de denuncias para solicitar "apoyo táctico" si el deudor te ha bloqueado o te esquiva en los pasillos.
*   ⚡ **Estética Cyber-Neon**: Efectos de resplandor (glow) neón magenta y ciano al enfocar campos, tipografías modernas (`Orbitron` e `Inter`) y sombras interactivas.

---

## 🛠️ Stack Tecnológico

*   **Backend**: Django 5.0.6 (Python 3)
*   **Base de Datos**: SQLite3 (Fresh y limpia)
*   **Procesamiento de Imágenes**: Pillow 12.2.0
*   **Frontend**: HTML5, Vanilla CSS3 (Custom `style.css`), Bootstrap 5.3.2 (Layout responsivo)

---

## 🚀 Instalación y Uso Local

Sigue estos sencillos pasos para levantar el entorno de desarrollo en tu computadora:

### 1. Clonar el repositorio
```bash
git clone https://github.com/Jos3alvarado/Proyecto_final_adakademy.git
cd Proyecto_final_adakademy
```

### 2. Crear y activar el entorno virtual
En Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```
En macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar las dependencias
```bash
pip install -r requirements.txt
```

### 4. Realizar las migraciones
```bash
python manage.py migrate
```

### 5. (Opcional) Poblar con datos de prueba humorísticos
Si deseas ver cómo luce la interfaz con registros de prueba precargados, puedes ejecutar nuestro comando personalizado:
```bash
python manage.py seed_debts
```
*Nota: Este comando creará 3 acreedores (`Jose`, `Pedro`, `Maria`) con sus respectivas deudas graciosas y capturas de evidencia generadas con Pillow.*

### 6. Iniciar el servidor de desarrollo
```bash
python manage.py runserver
```

Visita `http://127.0.0.1:8000/` en tu navegador para ver la cartelera de deudores.

---

## 🧪 Pruebas Unitarias

La aplicación cuenta con una suite completa de **8 pruebas unitarias** que validan la seguridad de la aplicación, el acceso al dashboard y los controles de privilegios:

```bash
python manage.py test
```

---

## ⚖️ Licencia

Desarrollado con fines educativos e informales en el curso de **Adakademy**. ¡Prohibido comerse la malta del compañero sin pagársela! 🕊️
