import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image
import os
from model_definition import EchoGuardCNN

def analyze_spectrogram(image_path: str) -> dict:
    print(f"🧠 PyTorch analyzing visual tensor: {image_path}...")
    
    # 1. Initialize the Neural Network
    model = EchoGuardCNN()
    
    # 2. Load trained weights (if they exist)
    weights_path = "echoguard_weights.pth"
    if os.path.exists(weights_path):
        model.load_state_dict(torch.load(weights_path, map_location=torch.device('cpu')))
        print("✅ Loaded trained model weights.")
    else:
        print("⚠️ No trained weights found. Using initialized network (untrained).")
    
    model.eval() # Set model to evaluation mode (shuts off Dropout)

    # 3. Preprocess the Spectrogram Image into a Tensor
    transform = transforms.Compose([
        transforms.Resize((128, 128)), # Standardize size for the CNN
        transforms.ToTensor(),         # Convert pixels to numbers between 0 and 1
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])
    
    try:
        # Load image, ensure it has 3 color channels (RGB), and apply transforms
        img = Image.open(image_path).convert('RGB')
        input_tensor = transform(img).unsqueeze(0) # Add batch dimension: [1, 3, 128, 128]
        
        # 4. Run the Inference!
        with torch.no_grad():
            output = model(input_tensor)
            probabilities = F.softmax(output, dim=1) 
            
            # Extract both raw scores so we can see inside the AI's brain
            fake_prob = probabilities[0][0].item() 
            real_prob = probabilities[0][1].item()
            
            # --- THE DEBUGGER ---
            print("="*40)
            print(f"🔍 AI RAW VISION FOR: {os.path.basename(image_path)}")
            print(f"🔴 FAKE SCORE: {fake_prob*100:.2f}%")
            print(f"🟢 REAL SCORE: {real_prob*100:.2f}%")
            print("="*40)
        
        # 5. Format the JSON Response
        if fake_prob > 0.60: # We moved the threshold back to a safe 60%
            return {
                "verdict": "Synthetic Audio (Deepfake)",
                "threat_score": round(fake_prob, 4),
                "ui_color": "red"
            }
        else:
            return {
                "verdict": "Authentic Human Voice",
                "threat_score": round(real_prob, 4), # UI now shows the real confidence
                "ui_color": "green"
            }
            
    except Exception as e:
        print(f"❌ PyTorch Inference Error: {e}")
        return {"verdict": "Error processing tensor", "threat_score": 0.0, "ui_color": "red"}