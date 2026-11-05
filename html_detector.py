from bs4 import BeautifulSoup
from text_detector import analyze_text

def analyze_html(html_code):
    if not html_code or not html_code.strip():
        return {"overall_ai_prob": 0.0, "verdict": "Нет HTML"}
    
    soup = BeautifulSoup(html_code, "html.parser")
    clean_text = soup.get_text(separator=" ")
    return analyze_text(clean_text)