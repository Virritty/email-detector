import pandas as pd
import json
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, roc_curve
import joblib

def train_baseline_model(data_path="train_data.csv"):
    df = pd.read_csv(data_path)
    
    X = df["text"].astype(str).tolist()
    y = df["label"].tolist()

    # Делим на обучающую 70 и 30 проц
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train_vec, y_train)

    print("\n4. Оценка качества на тестовой выборке:")
    y_pred = model.predict(X_test_vec)
    y_prob = model.predict_proba(X_test_vec)[:, 1]

    # Считаем все 4 метрики
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    try:
        roc_auc = roc_auc_score(y_test, y_prob)
    except ValueError:
        roc_auc = float("nan")

    print(f" - Precision: {precision:.4f}")
    print(f" - Recall:    {recall:.4f}")
    print(f" - F1 Score:  {f1:.4f}")
    print(f" - ROC AUC:   {roc_auc:.4f}")

    #cохраняем метрики в json
    metrics = {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4) if not str(roc_auc) == 'nan' else 0.0
    }
    with open("metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)
    print("Метрики сохранены в metrics.json")

    # Строим график ROC-кривой
    if not str(roc_auc) == 'nan':
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='blue', label=f'ROC-AUC = {roc_auc:.4f}')
        plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve - Text Detector')
        plt.legend(loc="lower right")
        plt.grid(True)
        plt.savefig("roc_curve.png")
        plt.close()
        print("График ROC-кривой сохранен в roc_curve.png")

    joblib.dump(model, "text_detector_model.pkl")
    joblib.dump(vectorizer, "tfidf_vectorizer.pkl")
    print("Файлы 'text_detector_model.pkl' и 'tfidf_vectorizer.pkl' созданы")

if __name__ == "__main__":
    train_baseline_model()