import openai
from gtts import gTTS
import os
from github import Github
import time

# Configurar la clave API de OpenAI
openai.api_key = "Tu clave api de Openai"

# Configurar el token de GitHub y el repositorio
GITHUB_TOKEN = "tu_token_github"
REPO_NAME = "usuario/repositorio"
ARCHIVO = "pregunta.txt"

def verificar_cambios_y_descargar(repo, archivo, sha_guardado):
    try:
        contenido_archivo = repo.get_contents(archivo)
        sha_actual = contenido_archivo.sha

        if sha_actual != sha_guardado:
            print("Se detectaron cambios en el archivo. Descargando...")
            with open(archivo, "w") as f:
                f.write(contenido_archivo.decoded_content.decode("utf-8"))

            # Guardar el nuevo SHA
            with open("ultimo_sha.txt", "w") as f:
                f.write(sha_actual)

            return True, sha_actual  # Cambios detectados y archivo descargado
        else:
            return False, sha_guardado
    except Exception as e:
        print(f"Error al verificar o descargar el archivo: {e}")
        return False, sha_guardado

def generar_respuesta(frase_usuario):
    prompt = f"Eres un robot SUMMIT XL. Genera una respuesta a la siguiente frase del usuario: {frase_usuario}"
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un robot llamado SUMMIT XL."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=350,
            temperature=0.7
        )
        return respuesta.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error al conectar con la API: {e}")
        return "Lo siento, no puedo generar una respuesta en este momento."

def convertir_a_audio(texto):
    try:
        tts = gTTS(text=texto, lang='es')
        archivo_audio = "respuesta.mp3"
        tts.save(archivo_audio)
        return archivo_audio
    except Exception as e:
        print(f"Error al convertir texto a audio: {e}")
        return None

def reproducir_audio(archivo_audio):
    try:
        os.system(f"start {archivo_audio}" if os.name == "nt" else f"afplay {archivo_audio}")
    except Exception as e:
        print(f"Error al reproducir el audio: {e}")

if __name__ == "__main__":
    # Inicializar conexión con GitHub
    github = Github(GITHUB_TOKEN)
    repo = github.get_repo(REPO_NAME)

    # Leer el SHA guardado
    try:
        with open("ultimo_sha.txt", "r") as f:
            sha_guardado = f.read().strip()
    except FileNotFoundError:
        sha_guardado = None  # No hay SHA previo

    while True:
        # Verificar cambios en el archivo
        cambios_detectados, sha_guardado = verificar_cambios_y_descargar(repo, ARCHIVO, sha_guardado)

        if cambios_detectados:
            try:
                with open(ARCHIVO, "r") as archivo_local:
                    pregunta = archivo_local.read().strip()

                print("Contenido de la pregunta:", pregunta)

                if os.path.exists("respuesta.mp3"):
                    os.remove("respuesta.mp3")

                respuesta = generar_respuesta(pregunta)
                print(f"SUMMIT XL responde: {respuesta}")

                archivo_audio = convertir_a_audio(respuesta)
                if archivo_audio:
                    reproducir_audio(archivo_audio)

            except Exception as e:
                print(f"Error al manejar el archivo descargado: {e}")

        time.sleep(5)  # Espera 5 segundos antes de verificar nuevamente
