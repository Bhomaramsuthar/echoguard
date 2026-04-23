from fastapi import FastAPI, UploadFile, File
import shutil
import os
from audio_processor import generate_spectrogram
from model_inference import analyze_spectrogram

app = FastAPI(title="EchoGuard API")

# Create temporary directories to hold files during processing
os.makedirs("temp_audio", exist_ok=True)
os.makedirs("temp_images", exist_ok=True)

@app.post("/analyze")
async def analyze_audio_endpoint(audio_file: UploadFile = File(...)):
    print(f"\n📥 Received file: {audio_file.filename}")
    
    # 1. Save the uploaded audio to a temporary file
    temp_audio_path = f"temp_audio/{audio_file.filename}"
    with open(temp_audio_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)
        
    # 2. Process Audio -> Image (Using the script you just tested)
    output_image_path = f"temp_images/spec_{audio_file.filename}.png"
    generated_image = generate_spectrogram(temp_audio_path, output_image_path)
    
    if not generated_image:
        return {"error": "Failed to generate spectrogram."}
        
    # 3. Analyze Image -> Threat Score (Using our dummy AI)
    # Set force_fake=True so you get a scary "Red" result for your PPT screenshot
    ai_result = analyze_spectrogram(generated_image)
    
    # 4. Cleanup (Delete the temp audio to save hard drive space)
    os.remove(temp_audio_path)
    
    # 5. Return the JSON payload to the frontend
    return {
        "filename": audio_file.filename,
        "analysis": ai_result,
        "spectrogram_path": generated_image
    }