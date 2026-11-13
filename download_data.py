from datasets import load_dataset
import pandas as pd

# Загружаем датасет
dataset = load_dataset("iitolstykh/LLMTrace_classification", split="train")
df = dataset.to_pandas()

# Берем и английский, и русский 
df = df[['text', 'label']] 

# Переводим метки в 0/1
df['label'] = df['label'].map({'human': 0, 'ai': 1})

# Берем, например, по 20-30 тысяч каждого языка, чтобы не обучать вечность
df_ru = df.head(20000) # В реальности лучше перемешать и взять равные доли, но для теста сойдет
df.to_csv("train_data.csv", index=False)
print("Готово, теперь в данных есть и английский.")