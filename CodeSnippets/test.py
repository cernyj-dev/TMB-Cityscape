import tkinter as tk
from PIL import Image, ImageTk

canvas = tk.Canvas(width = 640, height=480)
canvas.pack()

img = tk.PhotoImage(file='test_img.png')
#resize_image = img.resize((100, 100))
img = img.subsample(10,10)
canvas.create_image(10, 10, anchor=tk.NW,image=img)

canvas.mainloop()