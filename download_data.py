from datasets import load_dataset
import pandas as pd

print("Скачиваем")
dataset = load_dataset("iitolstykh/LLMTrace_classification", split="train")
df = dataset.to_pandas()

df = df[['text', 'label']]

df['label'] = df['label'].map({'human': 0, 'ai': 1})

# Берем 20 000 строк
df = df.head(20000)

# Сохраняем в CSV
df.to_csv("train_data.csv", index=False)
print("Файл train_data.csv создан")