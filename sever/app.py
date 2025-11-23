from flask import Flask, request, send_file, render_template, jsonify
import os
import time


from vision import analizar_imagen_desde_bytes
from tts_prueba import generar_audio

app = Flask(__name__)

# Rutas de archivos
LAST_IMAGE_PATH = "latest.jpg"
AUDIOS_DIR = "audios"
LAST_AUDIO_PATH = os.path.join(AUDIOS_DIR, "latest_audio.mp3")
DESC_PATH = "latest_desc.txt"

# Variable global para controlar cuándo hubo un cambio (para el frontend)
last_update_timestamp = int(time.time())

@app.route("/", methods=["GET"])
def index():
    """Renderiza el HTML bonito."""
    # Leemos la descripción actual
    descripcion = "Esperando primera imagen..."
    if os.path.exists(DESC_PATH):
        with open(DESC_PATH, "r", encoding="utf-8") as f:
            descripcion = f.read().strip()
    
    # Pasamos el timestamp actual y la descripción a la plantilla
    return render_template("index.html", timestamp=last_update_timestamp, descripcion=descripcion)

@app.route("/check_update", methods=["GET"])
def check_update():
    """El JavaScript llama aquí cada 2s para ver si hay novedades."""
    # Devolvemos también la descripción para actualizar el texto sin recargar
    descripcion = ""
    if os.path.exists(DESC_PATH):
        with open(DESC_PATH, "r", encoding="utf-8") as f:
            descripcion = f.read().strip()
            
    return jsonify({
        "timestamp": last_update_timestamp,
        "descripcion": descripcion
    })

@app.route("/image", methods=["GET"])
def get_image():
    if not os.path.exists(LAST_IMAGE_PATH):
        return "No hay imagen", 404
    return send_file(LAST_IMAGE_PATH, mimetype="image/jpeg")

@app.route("/audio", methods=["GET"])
def get_audio():
    if not os.path.exists(LAST_AUDIO_PATH):
        return "No hay audio", 404
    return send_file(LAST_AUDIO_PATH, mimetype="audio/mpeg")

@app.route("/upload", methods=["POST"])
def upload():
    global last_update_timestamp
    
    img_bytes = request.data
    if not img_bytes:
        return "No data", 400

    # 1. Guardar imagen
    with open(LAST_IMAGE_PATH, "wb") as f:
        f.write(img_bytes)
    print(f"[ESP32] Imagen recibida ({len(img_bytes)} bytes)")

    # 2. Gemini Vision
    try:
        descripcion = analizar_imagen_desde_bytes(img_bytes)
        print(f"[GEMINI] {descripcion}")
    except Exception as e:
        print(f"[ERROR GEMINI] {e}")
        descripcion = "Error analizando la imagen."

    with open(DESC_PATH, "w", encoding="utf-8") as f:
        f.write(descripcion)

    # 3. ElevenLabs TTS
    try:
        audio_bytes = generar_audio(descripcion)
        os.makedirs(AUDIOS_DIR, exist_ok=True)
        with open(LAST_AUDIO_PATH, "wb") as f:
            f.write(audio_bytes)
        print("[ELEVENLABS] Audio generado.")
    except Exception as e:
        print(f"[ERROR TTS] {e}")

    # 4. ACTUALIZAR TIMESTAMP
    # Esto avisa al frontend de que hay datos nuevos
    last_update_timestamp = int(time.time())

    return jsonify({"status": "ok", "descripcion": descripcion}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
