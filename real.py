import json
import re
from pathlib import Path

from docx import Document


def parse_docx(docx_path, images_dir="images"):
    # 1. Читаем и очищаем строки от пустых и мусорных
    doc = Document(docx_path)
    junk_pattern = r"^(СОГЛАСОВАНО|НА СОГЛАСОВАНИИ|[A-Z]\d{4}|[A-Z]\d{3}_\d{8}_[A-Z]\d{3})(,\s*[A-Z]\d{4})*$"

    lines = []
    for p in doc.paragraphs:
        text = p.text.strip()
        if text and not re.match(junk_pattern, text):
            lines.append(text)

    # Заготовки для распределения
    fav_names = ["Васильев", "Козырев", "Ажимов", "Секацкий", "Кирабаев", "Матвейчев"]
    fav_blocks = [None] * len(fav_names)  # Массив-пустышка для сохранения порядка
    reg_blocks = []

    # 2. Прямой обход по очищенным строкам
    i = 0
    while i < len(lines):
        if lines[i].isdigit():
            fio = lines[i + 1]
            desc = lines[i + 2]

            # Собираем цитату до следующего числа или конца списка
            quote_lines = []
            i += 3
            while i < len(lines) and not lines[i].isdigit():
                quote_lines.append(lines[i])
                i += 1
            # quote_text = " ".join(quote_lines)

            # Определяем пол и имя картинки
            fio_parts = fio.split()
            last_name = fio_parts[0] if fio_parts else ""
            patronymic = fio_parts[2] if len(fio_parts) > 2 else ""

            gender_placeholder = (
                "placeholder_female.png"
                if patronymic.endswith(("вна", "чна", "ична"))
                else "placeholder_male.png"
            )

            # Ищем файл картинки
            img_path = (
                list(Path(images_dir).glob(f"{' '.join(fio_parts)}.*"))
                if Path(images_dir).exists()
                else []
            )
            img_name = img_path[0].name if img_path else gender_placeholder

            # Формируем готовый блок
            block = {"name": fio, "desc": desc, "text": quote_lines, "img": img_name}

            # Распределяем по спискам
            if last_name in fav_names:
                if last_name in fav_names:
                    fav_blocks[fav_names.index(last_name)] = block
            else:
                reg_blocks.append(block)
        else:
            i += 1

    # Формируем финальный JSON
    result = {
        "fav": {"sym": False, "blocks": [b for b in fav_blocks if b is not None]},
        "reg": {"sym": False, "blocks": reg_blocks},
    }

    with open("data/real.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    parse_docx("data/data.docx")
