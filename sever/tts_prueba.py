from elevenlabs.client import ElevenLabs

API_KEY = "sk_6a42b6e69b27eac4e1cfcee878bcc439553c4cad168a4fde"
VOICE_ID = "m7yTemJqdIqrcNleANfX"

# Crea el cliente una vez
client = ElevenLabs(api_key=API_KEY)


def generar_audio(texto: str) -> bytes:
    """
    Convierte texto a voz usando ElevenLabs y devuelve los bytes del audio.
    """
    audio_stream = client.text_to_speech.convert(
        text=texto,
        voice_id=VOICE_ID,
        model_id="eleven_flash_v2_5",
        output_format="mp3_22050_32",
    )

    audio_bytes = b""
    for chunk in audio_stream:
        audio_bytes += chunk

    return audio_bytes


# PRUEBA OPCIONAL — esto NO se ejecuta cuando importas
if __name__ == "__main__":
    prueba = generar_audio("Prueba de voz en servidor Vultr.")

    with open("prueba_server.mp3", "wb") as f:
        f.write(prueba)

    print("Se generó prueba_server.mp3")
