import pytesseract
from PIL import Image
from transformers import MarianMTModel, MarianTokenizer
import tkinter as tk
import torch

try:
    import sentencepiece
except ImportError:
    raise ImportError("The SentencePiece library is required but not installed. Install it using 'pip install sentencepiece'.")

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

model_name = 'Helsinki-NLP/opus-mt-en-uk'
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.load_state_dict(torch.load("Fine-tuning/fine_tuned_weights.pth", map_location=device))
model.to(device)
model.eval()

def ocr_extract_text(image_path, lang='eng'):
    image = Image.open(image_path)
    try:
        text = pytesseract.image_to_string(image, lang=lang)
        text = text.replace("|", "I")
        return text
    except Exception as e:
        print(f"Помилка при розпізнаванні тексту: {e}")
        return ""

import re

def remove_newlines_and_structures(text):
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'(\s+•\s)', '\n• ', text)
    return text

def split_into_sentences(text):
    sentences = re.split(r'(?<=\.|\?|\!)\s+', text)
    return sentences

def translate_text(text, dest_language="uk"):
    try:
        if dest_language != "uk":
            raise ValueError(f"Невідома мова перекладу: {dest_language}")

        text = remove_newlines_and_structures(text)

        sentences = split_into_sentences(text)

        translated_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True).to(device)
                translated_tokens = model.generate(**inputs)
                translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
                translated_sentences.append(translated_text)

        return " ".join(translated_sentences)
    except Exception as e:
        print(f"Помилка при перекладі: {e}")
        return "Помилка перекладу"

def ocr_and_translate(image_path, dest_language="uk"):
    text = ocr_extract_text(image_path, lang='eng')
    print(f"Розпізнаний текст: {text}")
    print(f"Переклад тексту на {dest_language}...")
    translated_text = translate_text(text, dest_language)
    print(f"Перекладений текст: {translated_text}")

    return translated_text