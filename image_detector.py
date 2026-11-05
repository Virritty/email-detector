from transformers import pipeline
from PIL import Image
import os

print("Загрузка модели для картинок...")
detector = pipeline("image-classification", model="Ateeqq/ai-vs-human-image-detector")

def analyze_image(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        results = detector(img)
        ai_prob = 0.0
        for res in results:
            if "artificial" in res['label'].lower() or "ai" in res['label'].lower():
                ai_prob = res['score']
                break
        return {"ai_probability": round(ai_prob, 3), "is_ai": ai_prob >= 0.5}
    except Exception as e:
        return {"error": str(e)}