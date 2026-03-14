from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
import subprocess
import uuid
import os

app = FastAPI()

# --- استخراج صورة من الفيديو ---
@app.get("/thumbnail")
def get_thumbnail(url: str = Query(...), time: str = "00:01:00"):
    """
    - url: رابط الفيديو المباشر (MP4)
    - time: الوقت الذي تريد أخذ اللقطة منه (HH:MM:SS)
    """
    filename = f"thumb_{uuid.uuid4().hex}.jpg"

    command = [
        "ffmpeg",
        "-ss", time,
        "-i", url,
        "-frames:v", "1",
        "-y",
        filename
    ]

    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return FileResponse(filename, media_type="image/jpeg", filename=filename)
    except subprocess.CalledProcessError as e:
        return {"error": "فشل استخراج الصورة", "details": str(e)}
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# --- جلب مدة الحلقة ---
@app.get("/duration")
def get_duration(url: str = Query(...)):
    """
    - url: رابط الفيديو المباشر (MP4)
    - يعطي مدة الحلقة بالثواني وصيغة HH:MM:SS
    """
    command = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        url
    ]

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        duration_sec = float(result.stdout.strip())
        
        # تحويل الثواني إلى HH:MM:SS
        hours = int(duration_sec // 3600)
        minutes = int((duration_sec % 3600) // 60)
        seconds = int(duration_sec % 60)
        duration_hms = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        return {
            "duration_seconds": duration_sec,
            "duration_hms": duration_hms
        }

    except subprocess.CalledProcessError as e:
        return {"error": "فشل جلب مدة الفيديو", "details": str(e)}

# لتشغيل السيرفر محلياً
# uvicorn main:app --reload --host 0.0.0.0 --port 8000
