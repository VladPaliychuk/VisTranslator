import tkinter as tk
from tkinter import messagebox
import keyboard

def save_hotkey(hotkey):
    with open("config.txt", "w") as config_file:
        config_file.write(hotkey)
        
def open_settings():
    window = tk.Tk()
    window.title("Налаштування")

    window.configure(bg="#f7f7f7")

    hotkey_label = tk.Label(window, text="Комбінація клавіш:", font=("Arial", 11), bg="#f7f7f7", fg="#333")
    hotkey_label.pack(pady=(15, 5))

    hotkey_entry = tk.Entry(window, width=25, font=("Arial", 10), bd=1, relief="flat")
    hotkey_entry.pack(pady=(0, 10), padx=15)

    def save_hotkey_click():
        hotkey = hotkey_entry.get()
        if hotkey:
            try:
                keyboard.parse_hotkey(hotkey)
                save_hotkey(hotkey)
                messagebox.showinfo("Збережено", f"Комбінація '{hotkey}' збережена!")
                window.destroy()
            except ValueError:
                messagebox.showerror("Помилка", "Невірна комбінація клавіш. Спробуйте ще раз.")
        else:
            messagebox.showerror("Помилка", "Введіть комбінацію клавіш.")

    def record_hotkey():
        hotkey_entry.delete(0, tk.END)  
        record_button.config(text="Запис йде...", bg="#d9534f", fg="white", state="disabled")

        key = keyboard.read_hotkey(suppress=False)
        hotkey = "+".join(sorted(str(key).split("+"), reverse=True))
        hotkey_entry.insert(0, hotkey)
        save_hotkey(hotkey)
        record_button.config(text="Записати комбінацію", bg="#e0e0e0", fg="black", state="normal")
        messagebox.showinfo("Збережено", f"Комбінація '{hotkey}' збережена!")
        keyboard.unhook_all() 
        window.destroy()

    save_button = tk.Button(window, text="Зберегти комбінацію", command=save_hotkey_click, bg="#e0e0e0", fg="Black", font=("Arial", 10), bd=0, relief="flat")
    save_button.pack(pady=8, padx=15, fill="x")

    record_button = tk.Button(window, text="Записати комбінацію", command=record_hotkey, bg="#e0e0e0", fg="black", font=("Arial", 10), bd=0, relief="flat")
    record_button.pack(pady=8, padx=15, fill="x")

    window.mainloop()


def load_hotkey():
    try:
        with open("config.txt", "r") as config_file:
            hotkey = config_file.read().strip()
            return hotkey
    except FileNotFoundError:
        return None
