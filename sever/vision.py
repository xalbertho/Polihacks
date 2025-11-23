from google import genai
from google.genai import types

API_KEY = "!!!!TU_GEMINI-API_AQUI!!!!"
client = genai.Client(api_key=API_KEY)


def analizar_imagen_desde_bytes(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """
    Analiza una imagen directamente desde datos binarios (bytes),
    sin necesidad de guardarla en un archivo.
    """
    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type,
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            image_part,
            "Describe en una sola frase muy corta lo que ves en la imagen.Si ves un billete nombra se denomicacion. "
            "Habla en español. No agregues nada más.",
        ],
    )

    texto = getattr(response, "text", None)
    if texto:
        return texto.strip()

    # Fallback si Gemini responde raro
    if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if getattr(part, "text", None):
                return part.text.strip()

    print("Respuesta sin texto:")
    print(response)
    return "No pude interpretar la imagen."


def analizar_imagen(ruta_imagen: str, mime_type: str = "image/jpeg") -> str:
    """
    Versión cómoda que sigue aceptando ruta de archivo,
    pero por dentro usa analizar_imagen_desde_bytes.
    """
    with open(ruta_imagen, "rb") as f:
        image_bytes = f.read()

    return analizar_imagen_desde_bytes(image_bytes, mime_type)


if __name__ == "__main__":
    print(analizar_imagen("foto_prueba.jpg"))
