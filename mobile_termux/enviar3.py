import os
import time
import requests

WATCH_DIR = "/storage/emulated/O/DCIM/Camera/"  # carpeta donde la cámara guarda fotos
SERVER_URL = "http://96.30.196.163:4000/upload"
INTERVALO = 5  # segundos entre revisiones

VALID_EXTS = (".jpg", ".jpeg", ".JPG", ".JPEG")


def get_latest_image_path():
    """Regresa la ruta de la imagen más reciente en WATCH_DIR."""
    if not os.path.isdir(WATCH_DIR):
        print(f"[WARN] Carpeta no encontrada: {WATCH_DIR}")
        return None

    files = [
        os.path.join(WATCH_DIR, f)
        for f in os.listdir(WATCH_DIR)
        if f.endswith(VALID_EXTS)
    ]

    if not files:
        return None

    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return files[0]


def send_image(path):
    """Lee la imagen y la manda al servidor."""
    print(f"[DEBUG] Voy a leer la imagen: {path}")
    try:
        with open(path, "rb") as f:
            img_bytes = f.read()
    except Exception as e:
        print(f"[ERROR] No se pudo leer la imagen: {e}")
        return

    print(f"[DEBUG] Bytes leídos: {len(img_bytes)}")
    headers = {"Content-Type": "image/jpeg"}
    print(f"[DEBUG] Enviando a: {SERVER_URL}")

    try:
        resp = requests.post(
            SERVER_URL,
            data=img_bytes,
            headers=headers,
            timeout=15
        )
        print(f"[UPLOAD] Status: {resp.status_code}")
        print(f"[UPLOAD] Headers resp: {resp.headers}")
        try:
            print("[UPLOAD] Respuesta JSON:", resp.json())
        except Exception:
            print("[UPLOAD] Respuesta texto:", resp.text[:200])
    except Exception as e:
        print(f"[ERROR] Falló el POST: {repr(e)}")  # repr para ver el tipo de error


def main():
    print(f"Vigilando carpeta: {WATCH_DIR}")
    print(f"Revisando cada {INTERVALO} segundos.")
    print("Toma fotos normalmente con la app de cámara.\n")

    last_sent_path = None
    last_sent_mtime = 0.0

    while True:
        latest = get_latest_image_path()
        if latest is not None:
            mtime = os.path.getmtime(latest)

            if latest != last_sent_path and mtime > last_sent_mtime:
                print(f"[DETECTADO] Nueva foto: {latest} (mtime={mtime})")
                send_image(latest)
                last_sent_path = latest
                last_sent_mtime = mtime
        else:
            print("[DEBUG] No encontré imágenes aún.")

        time.sleep(INTERVALO)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSaliendo...")
