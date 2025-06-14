from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import speech_recognition as sr
import tempfile
import base64
import uvicorn
from fastapi import UploadFile, File
import subprocess


app = FastAPI()

class AudioBase64(BaseModel):
    audio_base64: str

@app.post("/transcribe/")
async def transcribe_audio(data: AudioBase64):
    try:
        audio_bytes = base64.b64decode(data.audio_base64)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": "Invalid base64 audio"})

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    recognizer = sr.Recognizer()
    with sr.AudioFile(tmp_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="es-ES")
    except sr.UnknownValueError:
        text = ""
    except sr.RequestError as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    return {"text": text}

@app.post("/transcribe-file/")
async def transcribe_audio_file(file: UploadFile = File(...)):
    if file.content_type not in ["audio/wav", "audio/x-wav", "audio/wave", "audio/vnd.wave"]:
        return JSONResponse(status_code=400, content={"error": "Invalid content type. Please upload a .wav file."})
    try:
        audio_bytes = await file.read()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Could not read file"})

    # Save the uploaded .wav file to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp_path_wav = tmp.name

    recognizer = sr.Recognizer()
    with sr.AudioFile(tmp_path_wav) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="es-ES")
    except sr.UnknownValueError:
        text = ""
    except sr.RequestError as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    return {"text": text}

@app.post("/transcribe-file-oga/")
async def transcribe_audio_file(file: UploadFile = File(...)):
    if file.content_type not in [
        "audio/wav", "audio/x-wav", "audio/wave", "audio/vnd.wave",
        "audio/ogg", "audio/oga", "audio/opus"
    ]:
        return JSONResponse(status_code=400, content={"error": "Invalid content type. Please upload a .wav or .oga file."})
    try:
        audio_bytes = await file.read()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Could not read file"})

    # Save the uploaded file to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".oga") as tmp:
        tmp.write(audio_bytes)
        tmp_path_oga = tmp.name

    # If the file is .oga or .ogg, convert to .wav
    if file.content_type in ["audio/ogg", "audio/oga", "audio/opus"]:
        try:
            tmp_path_wav = tmp_path_oga.replace(".oga", ".wav")
            # Use ffmpeg to convert .oga/.ogg/.opus to .wav
            subprocess.run(
                ["ffmpeg", "-y", "-i", tmp_path_oga, tmp_path_wav],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            return JSONResponse(status_code=500, content={"error": f"Audio conversion failed: {e.stderr.decode('utf-8')}"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": f"Unexpected error during conversion: {str(e)}"})
    else:
        tmp_path_wav = tmp_path_oga  # Already .wav

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(tmp_path_wav) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language="es-ES")
    except sr.UnknownValueError:
        text = ""
    except sr.RequestError as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error processing audio: {str(e)}"})

    return {"text": text}
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
