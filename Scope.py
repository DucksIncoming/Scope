from tkinter import *
from PIL import ImageTk, Image
import os

def createImage(root, imgPath, size):
    img = Image.open(imgPath)
    img = ImageTk.PhotoImage(img.resize(size)) 
    return img

def createImageLabel(root, imgPath, size):
    img = createImage(root, imgPath, size)
    label = Label(root, image=img, borderwidth=0)
    label.image = img
    return label

def createImageButton(root, imgPath, size, bCommand=None):
    img = createImage(root, imgPath, size) 
    button = Button(root, image=img, width=218, height=78, borderwidth=0, command=bCommand, relief="sunken", bd=0, highlightthickness=0)
    button.image = img
    return button

def sliderToggle():
    global enabled
    if (enabled):
        enabled = False
        img = createImage(root, "Images/slider_0.png", (220,80))
        sliderButton.config(image=img)
        sliderText.config(text="Disabled", foreground="#f78686")
        sliderButton.image = img
    else:
        enabled = True
        img = createImage(root, "Images/slider_1.png", (220,80))
        sliderButton.config(image=img)
        sliderText.config(text="Enabled", foreground="#b6d7a8")
        sliderButton.image = img

root = Tk()
root.title("Scope")
root.iconphoto(True, PhotoImage(file="Images/ico.png"))
root.resizable(width=False, height=False)

root.geometry("1050x637")
root["background"] = "#1e1e1e"

scopeImage = createImageLabel(root, "Images/scopeTitle.png", (220,120))
scopeImage.pack()

global enabled
enabled = False
sliderButton = createImageButton(root, "Images/slider_0.png", (220, 80), sliderToggle)
sliderButton.pack()

sliderText = Label(root, text="Disabled", font=("Roboto", 16), foreground="#f78686", background="#1e1e1e")
sliderText.config(anchor="center")
sliderText.place(x=480,y=185)

addRuleText = Label(root, text="Add New Rule", font=("Roboto", 24), foreground="white", background="#1e1e1e")
addRuleText.pack(pady=20)

selectedProgram = StringVar(root)
programList = OptionMenu(root, selectedProgram, "one", "two", "three")
programList.pack()

root.mainloop()