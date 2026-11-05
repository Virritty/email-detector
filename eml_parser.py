import os
import email
from email import policy
from email.header import decode_header

# Какие расширения считаем картинками
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff")

def decode_filename(raw_name):
    if not raw_name:
        return None

    parts = decode_header(raw_name)
    result = ""
    for content, encoding in parts:
        if isinstance(content, bytes):
            result += content.decode(encoding or "utf-8", errors="replace")
        else:
            result += content
    return result

def is_image_part(part):
    content_type = part.get_content_type()

    # 1. Явно указан image/*
    if content_type.startswith("image/"):
        return True

    # 2. Generic-тип, но расширение файла — картинка
    if content_type == "application/octet-stream":
        filename = decode_filename(part.get_filename())
        if filename and filename.lower().endswith(IMAGE_EXTENSIONS):
            return True

    return False

def parse_eml(filepath):
    result = {
        "subject": "",
        "text": "",
        "html": "",
        "images": []
    }

    # Открываем файл и парсим как email
    with open(filepath, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    # --- Извлекаем тему письма ---
    raw_subject = msg.get('subject')
    if raw_subject:
        subject_parts = decode_header(raw_subject)
        subject_text = ""
        for s_part, s_enc in subject_parts:
            if isinstance(s_part, bytes):
                subject_text += s_part.decode(s_enc or "utf-8", errors="replace")
            else:
                subject_text += s_part
        result["subject"] = subject_text

    # Создаём папку для картинок конкретного письма
    name = os.path.splitext(os.path.basename(filepath))[0]
    img_dir = os.path.join("output", name)
    os.makedirs(img_dir, exist_ok=True)

    # Проходим по всем частям письма
    for part in msg.walk():
        content_type = part.get_content_type()

        # 1. Текстовое тело
        if content_type == "text/plain":
            payload = part.get_payload(decode=True)
            if payload:
                result["text"] += payload.decode(part.get_content_charset() or "utf-8", errors="replace")

        # 2. HTML тело
        elif content_type == "text/html":
            payload = part.get_payload(decode=True)
            if payload:
                result["html"] += payload.decode(part.get_content_charset() or "utf-8", errors="replace")

        # 3. Картинки (вложения)
        elif is_image_part(part):
            raw_filename = part.get_filename()
            filename = decode_filename(raw_filename) or "image_unknown"
            img_path = os.path.join(img_dir, filename)

            img_data = part.get_payload(decode=True)
            if img_data:
                with open(img_path, "wb") as img:
                    img.write(img_data)
                result["images"].append(img_path)

    return result