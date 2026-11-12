import argparse
import json
import os
import glob
from eml_parser import parse_eml
from text_detector import analyze_text
from html_detector import analyze_html
from image_detector import analyze_image

THRESHOLD = 0.75

def analyze_single_email(filepath):
    try:
        # парсим письмо
        data = parse_eml(filepath)
        # анализ текста
        text_res = analyze_text(data["text"])
        # анализ html
        html_res = analyze_html(data["html"])
        # анализ темы
        subj_res = {"overall_ai_prob": 0.0, "verdict": "Нет темы"}
        if data["subject"]:
            subj_res = analyze_text(data["subject"])
        # анализ картинок
        images_results = []
        for img_path in data["images"]:
            img_res = analyze_image(img_path)
            images_results.append({
                "filename": os.path.basename(img_path),
                "ai_probability": img_res.get("ai_probability", 0.0),
                "is_ai": img_res.get("is_ai", False)
            })
        # берем максимальную вероятность из текста, html и темы
        scores = [text_res["overall_ai_prob"], html_res["overall_ai_prob"], subj_res["overall_ai_prob"]]
        overall_score = max(scores) if scores else 0.0
        
        verdict = "AI-Generated" if overall_score >= THRESHOLD else "Human-Written"
        
        # собираем объяснение
        explanation = f"Вердикт: {verdict}. Индекс AI: {overall_score:.2f}. "
        if text_res["overall_ai_prob"] >= THRESHOLD:
            explanation += "Тело письма содержит шаблонные фразы"
            
            # Вытаскиваем ключевые слова
            if text_res.get("top_words"):
                words_str = ", ".join([f"'{w}'" for w in text_res["top_words"]])
                explanation += f"Ключевые маркеры ИИ: {words_str}. "
                
        if html_res["overall_ai_prob"] >= THRESHOLD:
            explanation += "В HTML-разметке обнаружены признаки генерации. "
        if any(img["is_ai"] for img in images_results):
            explanation += "Обнаружены сгенерированные изображения. "

        result = {
            "file_id": os.path.basename(filepath),
            "overall_score": round(overall_score, 3),
            "verdict": verdict,
            "explanation": explanation.strip(),
            "zones": {
                "subject": {"score": subj_res["overall_ai_prob"], "verdict": subj_res["verdict"]},
                "text_body": {"score": text_res["overall_ai_prob"], "verdict": text_res["verdict"]},
                "html_body": {"score": html_res["overall_ai_prob"], "verdict": html_res["verdict"]},
                "images": images_results
            }
        }
        
        return result

    except Exception as e:
        # если файл битый — возвращаем ошибку
        return {
            "file_id": os.path.basename(filepath),
            "overall_score": 0.0,
            "verdict": "Error",
            "explanation": f"Ошибка разбора: {str(e)}",
            "zones": {}
        }

def save_json(data, output_path):
    if os.path.dirname(output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


parser = argparse.ArgumentParser(description="AI Email Detector")
parser.add_argument("--file", type=str, help="Один файл")
parser.add_argument("--dir", type=str, help="Папка с файлами")
parser.add_argument("--out", type=str, default="results", help="Куда сохранять")
    
args = parser.parse_args()

if args.file:
    print(f"Анализ файла: {args.file}...")
    result = analyze_single_email(args.file)
        
    if result["verdict"] == "Error":
        print(f"Ошибка: {result['explanation']}")
    else:
        print(f"Вердикт: {result['verdict']}")
        print(f"Индекс ИИ: {result['overall_score']}")
        print(f"Объяснение: {result['explanation']}")

        out_path = os.path.join(args.out, result["file_id"] + ".json")
        save_json(result, out_path)
        print(f"Сохранено в {out_path}")

elif args.dir:
    print(f"Анализ папки: {args.dir}...")
    files = glob.glob(os.path.join(args.dir, "*.eml"))
        
    if not files:
        raise SystemExit("Нет файлов .eml")

    summary = {}
    for f in files:
        try:
            result = analyze_single_email(f)
                
            if result["verdict"] == "Error":
                print(f"[-] {result['file_id']}: {result['explanation']}")
                continue
                    
            summary[result["file_id"]] = result
                
            out_path = os.path.join(args.out, "batch", result["file_id"] + ".json")
            save_json(result, out_path)
                
            print(f"[+] {result['file_id']}: {result['verdict']} ({result['overall_score']})")
        except Exception as e:
            print(f"[-] Ошибка с {f}: {e}")
        
    save_json(summary, os.path.join(args.out, "batch_summary.json"))
    print(f"Готово. Сводный файл: {args.out}/batch_summary.json")

else:
    print("Укажи --file или --dir")
