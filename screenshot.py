import tempfile
import tkinter as tk
from PIL import ImageGrab
import pyautogui

class ScreenshotApp:
    def __init__(self):
        self.root = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.canvas = None
        self.rect = None
        self.path = None

    def take_screenshot(self):
        self.create_dimmed_window()  

        self.root.bind("<ButtonPress-1>", self.on_button_press)
        self.root.bind("<ButtonRelease-1>", self.on_button_release)
        self.root.bind("<Motion>", self.on_mouse_move)
        self.root.mainloop()
        return self.path

    def create_dimmed_window(self):
        self.root = tk.Tk()
        self.root.attributes("-topmost", True)  
        self.root.geometry("{0}x{1}+0+0".format(self.root.winfo_screenwidth(), 
                                                self.root.winfo_screenheight()))  
        self.root.attributes("-alpha", 0.15)  
        self.root.overrideredirect(True) 
        self.root.configure(bg="gray")  

        self.canvas = tk.Canvas(self.root, bg='gray', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='black', 
                                                 width=2, dash=(2, 2), fill='white', tag='screenshot_rect')

    def on_mouse_move(self, event):
        if self.rect is not None:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        self.end_x = event.x
        self.end_y = event.y

        self.take_and_save_screenshot()  
        self.root.destroy() 

    def take_and_save_screenshot(self):
        x1 = self.root.winfo_rootx() + min(self.start_x, self.end_x)
        y1 = self.root.winfo_rooty() + min(self.start_y, self.end_y)
        x2 = self.root.winfo_rootx() + max(self.start_x, self.end_x)
        y2 = self.root.winfo_rooty() + max(self.start_y, self.end_y)

        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile:
            screenshot.save(tmpfile.name)
            print(f"Скріншот збережено як тимчасовий файл: {tmpfile.name}")
            self.path = tmpfile.name
