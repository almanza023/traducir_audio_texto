from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import speech_recognition as sr
import tempfile
import base64
import uvicorn

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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
