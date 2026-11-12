## Запуск
Нужен установленный и запущенный Docker Desktop.

### 1. Собрать образ
```bash
docker compose build
```

### 2. Обучить модель
Обязательно перед первым запуском, создаёт файлы `*.pkl`. Выберите один из вариантов.

**Вариант А — на своём датасете**

Положите в папку проекта файл `train_data.csv` с двумя колонками:

| text | label |
|---|---|
| Текст письма... | 0 |
| Другой текст... | 1 |

`text` — текст, `label` — `0` (написал человек) или `1` (сгенерировал ИИ).

Запустите обучение:
```bash
docker compose run --rm --entrypoint python train train_detector.py
```

**Вариант Б — на готовом датасете из интернета**

Датасет [LLMTrace](https://huggingface.co/datasets/iitolstykh/LLMTrace_classification) скачается автоматически:
```bash
docker compose run --rm train
```
Внимание: эта команда перезапишет файл `train_data.csv`, если он уже есть.

После обучения в папке появятся `metrics.json` (метрики качества) и `roc_curve.png` (ROC-кривая).

### 3. Проверить письма
Положите письма `.eml` в папку `samples/` и запустите:
```bash
docker compose up detector
```
Результаты сохраняются в папку `results/`.

Проверить одно письмо:
```bash
docker compose run --rm detector --file samples/letter.eml
```

## Формат результата

Для каждого письма создаётся JSON такого вида (значения условные):

```json
{
    "file_id": "letter.eml",
    "overall_score": 0.812,
    "verdict": "AI-Generated",
    "explanation": "Вердикт: AI-Generated. Индекс AI: 0.81. ...",
    "zones": {
        "subject":   {"score": 0.43, "verdict": "Человек"},
        "text_body": {"score": 0.812, "verdict": "ИИ"},
        "html_body": {"score": 0.0, "verdict": "Нет HTML"},
        "images": []
    }
}
```
