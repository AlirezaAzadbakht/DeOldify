import tempfile
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io
import warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*?Your .*? set is empty.*?")
from deoldify import device
from deoldify.device_id import DeviceId
device.set(device=DeviceId.GPU0)

from deoldify.visualize import get_image_colorizer
colorizer = get_image_colorizer(artistic=True)

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # or you can specify methods like ["GET", "POST"]
    allow_headers=["*"],
)
@app.post("/process")
async def process_image(file: UploadFile = File(...), render_factor: int=35):
    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        contents = await file.read()
        temp_file.write(contents)
        temp_file.seek(0)
        img = colorizer.get_transformed_image(path=temp_file.name, render_factor=render_factor, watermarked=False)
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/jpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5151)