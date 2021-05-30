import tkinter as tk
import Neura
from PIL import ImageGrab
import win32gui
import numpy
import matplotlib.pyplot


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.x = self.y = 0

        # Создание элементов
        self.canvas = tk.Canvas(self, width=300, height=300, bg="black", cursor="cross")
        self.label = tk.Label(self, text="¯\_(ツ)_/¯", font=("Helvetica", 48))
        self.identify_btn = tk.Button(self, text="Распознать", command=self.identify_handwriting)
        self.button_clear = tk.Button(self, text="Очистить", command=self.clear_all, background='Red')
        self.button_show = tk.Button(self, text="Показать", command=self.show_number, background='Grey')

        # Сетка окна
        self.canvas.grid(row=0, column=0, pady=2, sticky='W')
        self.label.grid(row=0, column=1, pady=2, padx=2)
        self.identify_btn.grid(row=1, column=1, pady=2, padx=2)
        self.button_clear.grid(row=1, column=0, pady=2)
        self.button_show.grid(row=1, column=2, pady=2)

        self.canvas.bind("<B1-Motion>", self.draw_lines)

    def clear_all(self):
        self.canvas.delete("all")

    def identify_handwriting(self):
        HWND = self.canvas.winfo_id()
        rect = win32gui.GetWindowRect(HWND)  # получаем координату холста
        img = ImageGrab.grab(rect)
        img = img.resize((28, 28))
        img = img.convert('L')
        img = numpy.array(img)
        img[img == 33] = 0
        img[img == 61] = 0
        img[img > 45] = 255
        img[img != 255] = 0

        neura = Neura.neuralNetwork()
        digit, percent = Neura.Identify(neura, img)
        print(self.label.configure(text=str(digit) + ', ' + str(percent) + '%'))

    def draw_lines(self, event):
        self.x = event.x
        self.y = event.y
        r = 10
        self.canvas.create_oval(self.x - r, self.y - r, self.x + r, self.y + r, fill='white', outline='white')

    def show_number(self):
        HWND = self.canvas.winfo_id()
        rect = win32gui.GetWindowRect(HWND)
        img = ImageGrab.grab(rect)
        img = img.resize((28, 28))
        img = img.convert('L')
        img = numpy.array(img)
        img[img == 33] = 0
        img[img == 61] = 0
        img[img > 65] = 255
        img[img != 255] = 0

        matplotlib.pyplot.imshow(img, cmap='Greys', interpolation=None)
        matplotlib.pyplot.show()


app = App()
tk.mainloop()
