# insAIght

Asistente de visión accesible que combina un ESP32-CAM o la cámara del móvil con un servidor Flask. El sistema describe imágenes con Gemini, genera audio con ElevenLabs y ofrece una interfaz web simple para escuchar y ver el resultado.

## 🔍 ¿Qué hace?
- **Captura**: toma fotos desde un ESP32-CAM (`device_esp32/`) o desde el móvil Android (script de Termux).
- **Envía**: las imágenes se mandan al servidor Flask vía `/upload`.
- **Procesa**: Gemini analiza la foto y devuelve una descripción breve en español.
- **Habla**: ElevenLabs convierte la descripción en audio (MP3).
- **Muestra**: la página web en `/app` actualiza imagen, texto y audio automáticamente.

## 📂 Estructura del proyecto
| Carpeta/archivo | Propósito |
| --- | --- |
| `sever/` | Backend Flask, plantillas y dependencias. Usa Gemini y ElevenLabs. |
| `static/` | Iconos e imágenes estáticas para la web. |
| `device_esp32/` | Sketch para ESP32-CAM (Arduino) que captura y envía fotos. |
| `mobile_termux/enviar3.py` | Script para Android + Termux: vigila la galería y sube la última foto al servidor. |

## 🚀 Puesta en marcha del servidor
1. Posiciónate en la carpeta `sever`:
   ```bash
   cd sever
   ```
2. Crea un entorno virtual e instala dependencias:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Configura tus claves en `vision.py` y `tts_prueba.py`:
   - `API_KEY` de Gemini (Google AI Studio).
   - `API_KEY` y `VOICE_ID` de ElevenLabs.
4. Ejecuta el servidor Flask:
   ```bash
   python app.py
   ```
5. Abre la interfaz:
   - `http://localhost:4000/` para ver el menú.
   - `http://localhost:4000/app` para la demo en vivo.

> El servidor guarda la última imagen en `latest.jpg`, la descripción en `latest_desc.txt` y el audio en `audios/latest_audio.mp3`.

## 📲 Envío de imágenes desde Android (Termux)
1. Copia `mobile_termux/enviar3.py` al teléfono.
2. Ajusta en el archivo:
   - `WATCH_DIR` (ruta donde la cámara guarda las fotos).
   - `SERVER_URL` (URL pública o LAN del servidor Flask con `/upload`).
3. Instala dependencias en Termux:
   ```bash
   pkg install python
   pip install requests
   ```
4. Ejecuta el script y toma fotos; cada imagen nueva se sube automáticamente:
   ```bash
   python enviar3.py
   ```

## 📡 Envío de imágenes desde ESP32-CAM
- Carga el sketch de `device_esp32/` en el ESP32-CAM con el IDE de Arduino.
- Configura tus credenciales Wi‑Fi y la URL del servidor (endpoint `/upload`).
- Al capturar, el módulo enviará la imagen como bytes al backend.

## 🌐 Endpoints clave
- `GET /` – Página de bienvenida.
- `GET /app` – Interfaz que muestra la última imagen, texto y audio.
- `POST /upload` – Recibe la imagen en el cuerpo de la solicitud.
- `GET /image` – Devuelve `latest.jpg`.
- `GET /audio` – Devuelve `audios/latest_audio.mp3`.
- `GET /check_update` – Devuelve `timestamp` y descripción para refrescar el frontend.

## 💡 Consejos visuales
- Usa `static/eye.png` como favicon y `static/logo.png` en presentaciones.
- La UI está en `sever/templates/app.html` y `home.html`; puedes modificar colores y tipografía ahí.

## 🧪 Pruebas rápidas
- Prueba manual: envía un JPEG con `curl` y verifica que la página `/app` se actualiza.
  ```bash
  curl -X POST --data-binary @tu_imagen.jpg http://localhost:4000/upload -H "Content-Type: image/jpeg"
  ```
- Si no ves audio o descripción, revisa que las API keys estén configuradas y que el servidor tenga salida a internet.

## 🧱 Stack
- **Flask** para el backend y plantillas.
- **Google Gemini** (vía `google-genai`) para visión y descripción.
- **ElevenLabs** para síntesis de voz.
- **Arduino / ESP32-CAM** y **Termux** como fuentes de imágenes.
