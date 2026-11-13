import re
import joblib
import numpy as np

# Загружаем сохраненную модель и векторизатор
model = joblib.load("text_detector_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")

# Словарь слов считаем один раз при загрузке, а не при каждом вызове (так быстрее)
feature_names = vectorizer.get_feature_names_out()

def split_into_sentences(text: str):
    raw_sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in raw_sentences if s.strip()]

def get_top_ai_words(text: str, top_n: int = 5):
    # Вытаскиваем слова, которые модель считает самыми иишными
    if not text.strip():
        return []
    
    # Векторизуем текст
    vec = vectorizer.transform([text])
    
    # Получаем индексы слов, которые вообще есть в тексте
    non_zero_indices = vec.nonzero()[1]
    
    if len(non_zero_indices) == 0:
        return []
        
    # Берем веса (коэффициенты) модели для этих слов
    coefs = model.coef_[0]
    
    # Сортируем слова по весу (чем больше, тем сильнее тянет в сторону ИИ)
    word_weights = [(feature_names[i], coefs[i]) for i in non_zero_indices]
    word_weights.sort(key=lambda x: x[1], reverse=True)
    
    # Возвращаем топ-N слов с положительным весом (те, что указывают на ИИ)
    top_words = [word for word, weight in word_weights if weight > 0][:top_n]
    return top_words

def analyze_text(text: str, threshold: float = 0.5):
    if not text or not text.strip():
        return {
            "overall_ai_prob": 0.0,
            "verdict": "Пустой текст",
            "total_sentences": 0,
            "suspicious_sentences_count": 0,
            "sentences": []
        }

    sentences = split_into_sentences(text)
    if not sentences:
        sentences = [text.strip()]

    sentence_results = []
    ai_probs = []

    for sentence in sentences:
        vec = vectorizer.transform([sentence])
        prob = float(model.predict_proba(vec)[0][1])
        ai_probs.append(prob)

        sentence_results.append({
            "sentence": sentence,
            "ai_probability": round(prob, 3),
            "is_ai": prob >= threshold
        })

    # Общую оценку считаем по всему тексту целиком — так же, как модель обучалась.
    # Оценки отдельных предложений оставляем только для подробного отчёта.
    overall_prob = float(model.predict_proba(vectorizer.transform([text]))[0][1])

    # Ищем ключевые слова, если текст похож на ИИ
    top_words = []
    if overall_prob >= threshold:
        top_words = get_top_ai_words(text)

    return {
        "overall_ai_prob": round(overall_prob, 3),
        "verdict": "ИИ" if overall_prob >= threshold else "Человек",
        "total_sentences": len(sentence_results),
        "suspicious_sentences_count": sum(1 for s in sentence_results if s["is_ai"]),
        "sentences": sentence_results,
        "top_words": top_words
    }