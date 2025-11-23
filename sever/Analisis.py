import os
from vision import analizar_imagen, analizar_imagen_desde_bytes
from tts_prueba import generar_audio


def analizar_y_guardar_audio(ruta_imagen: str, nombre_archivo: str = None) -> str:
    """
    Versión antigua: recibe ruta de imagen, genera audio y lo guarda.
    """
    descripcion = analizar_imagen(ruta_imagen)
    print("Descripción de la imagen:", descripcion)

    audio_bytes = generar_audio(descripcion)

    carpeta = "audios"
    os.makedirs(carpeta, exist_ok=True)

    if nombre_archivo is None:
        base = os.path.splitext(os.path.basename(ruta_imagen))[0]
        nombre_archivo = base + ".mp3"

    ruta_salida = os.path.join(carpeta, nombre_archivo)

    with open(ruta_salida, "wb") as f:
        f.write(audio_bytes)

    print("Audio guardado en:", ruta_salida)
    return ruta_salida


def analizar_y_guardar_audio_desde_bytes(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    nombre_archivo: str = "desde_bytes.mp3",
) -> str:
    """
    Nueva versión: recibe LA IMAGEN EN BYTES (como la mandaría la ESP32),
    analiza con Gemini, genera audio y lo guarda en audios/.
    """
    # 1) Imagen (bytes) -> texto
    descripcion = analizar_imagen_desde_bytes(image_bytes, mime_type=mime_type)
    print("Descripción de la imagen (desde bytes):", descripcion)

    # 2) Texto -> audio
    audio_bytes = generar_audio(descripcion)

    # 3) Guardar en audios/
    carpeta = "audios"
    os.makedirs(carpeta, exist_ok=True)

    ruta_salida = os.path.join(carpeta, nombre_archivo)

    with open(ruta_salida, "wb") as f:
        f.write(audio_bytes)

    print("Audio guardado en:", ruta_salida)
    return ruta_salida


if __name__ == "__main__":
    # Prueba antigua (por ruta)
    analizar_y_guardar_audio("foto_prueba.jpg")
