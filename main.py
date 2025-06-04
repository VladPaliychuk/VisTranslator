import tkinter as tk
from tkinter import messagebox
import keyboard
import threading
import os

from ocr_translation import ocr_extract_text, ocr_and_translate, remove_newlines_and_structures
from screenshot import ScreenshotApp
from settings import load_hotkey, open_settings
import pystray
from PIL import Image as PILImage
from pystray import MenuItem as item

class ScreenshotAppWithHotkey:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self.selected_language = tk.StringVar(self.root)
        self.selected_language.set("uk")

        self.screenshot_app = ScreenshotApp()
        self.hotkey = load_hotkey()

        if not self.hotkey:
            print("Не знайдено налаштувань. Відкриваємо панель налаштувань...")
            open_settings()

            self.root.update()
            self.hotkey = load_hotkey()

        if self.hotkey:
            self.set_hotkey()

        self.icon = self.create_tray_icon()
        threading.Thread(target=self.icon.run, args=(self.setup_icon,)).start()

    def set_hotkey(self):
        keyboard.unhook_all()
        print(f"\nВстановлено комбінацію клавіш: {self.hotkey}")
        keyboard.add_hotkey(self.hotkey, self.take_screenshot)
        print("Очікування натискання гарячої клавіші...")

    def take_screenshot(self):
        print("Гарячий клавіш натиснуто! Захоплення екрану...")
        # Захоплення екрану
        screenshot_path = self.screenshot_app.take_screenshot()

        if screenshot_path and os.path.exists(screenshot_path):
            threading.Thread(target=self.process_translation, args=(screenshot_path,)).start()
        else:
            print("Помилка: Скріншот не збережено або файл не існує.")

        self.set_hotkey()  

    def process_translation(self, screenshot_path):
        text = ocr_extract_text(screenshot_path)
        self.show_text_window(text, "Обробка запиту...")
        translated_text = ocr_and_translate(screenshot_path, self.selected_language.get())
        self.update_text_window(translated_text)

    def show_text_window(self, text, translated_text):
        self.text_window = tk.Toplevel(self.root)
        self.text_window.title("Розпізнаний текст")
        self.text_window.attributes("-topmost", True)

        x, y = self.root.winfo_pointerxy()
        self.text_window.geometry(f"+{x + 10}+{y + 10}")

        self.text_window.configure(bg="#2f3136", highlightthickness=1, highlightbackground="#8B4513")

        style_label = {"font": ("Arial", 10, "bold"), "bg": "#2f3136", "fg": "white"}

        original_label = tk.Label(self.text_window, text="Оригінал:", **style_label)
        original_label.pack(padx=5, pady=(5, 0))

        # Textbox style
        self.original_textbox = tk.Text(
            self.text_window,
            wrap=tk.WORD,
            height=10,
            width=60,
            font=("Arial", 10),
            bd=0,
            bg="#36393f",
            fg="white",
            insertbackground="white"
        )
        text = remove_newlines_and_structures(text)
        self.original_textbox.insert("1.0", text)
        self.original_textbox.pack(fill="both", padx=5, pady=5)
        self.original_textbox.config(state=tk.DISABLED)

        translated_label = tk.Label(self.text_window, text="Переклад:", **style_label)
        translated_label.pack(padx=5, pady=(5, 0))

        self.translated_textbox = tk.Text(
            self.text_window,
            wrap=tk.WORD,
            height=10,
            width=60,
            font=("Arial", 10),
            bd=0,
            bg="#36393f",
            fg="white",
            insertbackground="white"
        )
        self.translated_textbox.insert("1.0", translated_text)
        self.translated_textbox.pack(fill="both", padx=5, pady=5)
        self.translated_textbox.config(state=tk.DISABLED)

        # Button frame
        button_frame = tk.Frame(self.text_window, bg="#2f3136")
        button_frame.pack(fill="x", padx=5, pady=5)

        copy_original_button = tk.Button(
            button_frame,
            text="Копіювати оригінал",
            command=self.copy_to_clipboard,
            relief="flat",
            bg="#4f545c",
            fg="white",
            font=("Arial", 9)
        )
        copy_original_button.pack(side="left", padx=5)

        copy_translated_button = tk.Button(
            button_frame,
            text="Копіювати переклад",
            command=self.copy_translated_to_clipboard,
            relief="flat",
            bg="#4f545c",
            fg="white",
            font=("Arial", 9)
        )
        copy_translated_button.pack(side="left", padx=5)

        self.text_window.minsize(650, 400)

    def update_text_window(self, translated_text):
        self.translated_textbox.config(state=tk.NORMAL)
        self.translated_textbox.delete("1.0", tk.END)
        self.translated_textbox.insert("1.0", translated_text)
        self.translated_textbox.config(state=tk.DISABLED)

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.original_textbox.get("1.0", tk.END))
        self.root.update()

    def copy_translated_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.translated_textbox.get("1.0", tk.END))
        self.root.update()

    def create_tray_icon(self):
        image = PILImage.open("assets/icon.ico")
        menu = (
            item('Налаштування', self.open_settings),
            item('Вийти', self.quit_app),
        )
        icon = pystray.Icon("screenshot_app", image, "Скріншот і переклад", menu)
        return icon

    def open_settings(self, icon=None, item=None):
        open_settings()
        self.hotkey = load_hotkey()
        if self.hotkey:  
            self.set_hotkey()

    def setup_icon(self, icon):
        icon.visible = True

    def quit_app(self, icon, item):
        icon.stop()
        self.root.quit()

if __name__ == "__main__":
    app = ScreenshotAppWithHotkey()
    tk.mainloop()
