from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from datetime import date
from tkinter import messagebox
import json
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
    button = Button(root, image=img, width=size[0]-2, height=size[1]-2, borderwidth=0, command=bCommand, relief="sunken", bd=0, highlightthickness=0, cursor="hand2")
    button.image = img
    return button

def settingsToggle():
    pass

def behaviorSelect():
    pass

def refreshRuleTree():
    ruleTree.delete(*ruleTree.get_children())
    rules = getActiveRules()
    for i in range (len(rules[0])):
        textBehavior = "Mute on Lost Focus"
        if (bool(rules[1][i])):
            textBehavior = "Mute on Enter Focus"
        ruleTree.insert('', 'end', text=str(i), values=(rules[0][i], textBehavior, rules[2][i]))

def addRule():
    with open("rules.json") as rFile:
        data = json.load(rFile)
        tempData = data["rules"]
        if (selectedProgram.get() == "Select Program"):
            return
        tempData[selectedProgram.get()] = {"behavior": behavior.get(), "date": str(date.today())}
    with open("rules.json", "w") as f:
        json.dump(data, f, indent=4)

    refreshRuleTree()

def getActiveRules():
    programs = []
    behaviors = []
    dates = []

    with open("rules.json") as rFile:
        data = json.load(rFile)
        data = data["rules"]
        for rule in data:
            tempData = data[rule]
            programs.append(rule)
            behaviors.append(tempData["behavior"])
            dates.append(tempData["date"])
        return [programs, behaviors, dates]

def edit():
    currentItem = ruleTree.focus()
    currentItem = ruleTree.item(currentItem)
    try:
        selectedProgram.set(currentItem["values"][0])
    except:
        pass

def delete():
    currentItem = ruleTree.focus()
    currentItem = ruleTree.item(currentItem)
    try:
        delResponse = messagebox.askyesno("Scope", "Delete rule for '" + str(currentItem["values"][0]) + "'?")
        if (delResponse):
            with open('rules.json') as in_file:
                data = json.load(in_file)
                tempData = data["rules"]
                for element in tempData:
                    if (str(element) == currentItem["values"][0]):
                        del data["rules"][element]
                        break
                with open("rules.json", "w") as f:
                    json.dump(data, f, indent=4)
            refreshRuleTree()
    except:
        pass

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

# Base window setup
root = Tk()
root.title("Scope")
root.iconphoto(True, PhotoImage(file="Images/ico.png"))
root.resizable(width=False, height=False)
root.geometry("1050x700")
root["background"] = "#1e1e1e"

# Style stuff
style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", rowheight=40, )

# Settings icon
settingsButton = createImageButton(root, "Images/settings.png", (50,50), settingsToggle)
settingsButton.place(x=10, y=10)

# Scope Title at top of page
scopeImage = createImageLabel(root, "Images/scopeTitle.png", (220,120))
scopeImage.pack()

# Enabled/Disabled slider
global enabled
enabled = False
sliderButton = createImageButton(root, "Images/slider_0.png", (220, 80), sliderToggle)
sliderButton.pack()

# Enabled/disabled text
sliderText = Label(root, text="Disabled", font=("Roboto", 16), foreground="#f78686", background="#1e1e1e")
sliderText.config(anchor="center")
sliderText.place(x=480,y=185)

# Add rule label text
addRuleText = Label(root, text="Add New Rule", font=("Roboto", 24), foreground="white", background="#1e1e1e")
addRuleText.pack(pady=20)

# Program label text
programLabel = Label(root, text="Program", font=("Roboto", 18), foreground="#CECECE", background="#1e1e1e")
programLabel.place(x=210, y=260)

# Program dropdown menu
programs = ["program1","program2","program3"]
selectedProgram = StringVar(root)
selectedProgram.set("Select Program")
programList = ttk.Combobox(root, values=programs, state="readonly", textvariable=selectedProgram)
programList.config(width=100)
programList.pack(pady=20)

# Behavior label text
behaviorLabel = Label(root, text="Behavior", font=("Roboto", 18), foreground="#CECECE", background="#1e1e1e")
behaviorLabel.place(x=210, y=335)

# Behavior radio button options
behavior = IntVar(root)
lostFocusSelector = Radiobutton(root, text="Mute on Lost Focus", value=0, variable=behavior, background="#1e1e1e", activebackground="#1e1e1e", foreground="white", activeforeground="white", command=behaviorSelect, selectcolor="black", font=("Roboto", 12), cursor="hand2")
enterFocusSelector = Radiobutton(root, text="Mute on Enter Focus", value=1, variable=behavior, background="#1e1e1e", activebackground="#1e1e1e", foreground="white", activeforeground="white", command=behaviorSelect, selectcolor="black", font=("Roboto", 12), cursor="hand2")
lostFocusSelector.place(x=210, y=370)
enterFocusSelector.place(x=210, y=400)

# Add rule button
addRuleButton = createImageButton(root, "Images/addRule.png", (183, 68), bCommand=addRule)
addRuleButton.place(x=430, y=400)

# Existing rules box
ruleTree = ttk.Treeview(root, column=("id", "behavior", "date"), show="headings")
rules = getActiveRules()
ruleTreeWidth = 900

ruleTree.column("# 1", anchor=W, width=int(ruleTreeWidth/3), stretch=0)
ruleTree.heading("# 1", text="Program ID")
ruleTree.column("# 2", anchor=CENTER, width=int(ruleTreeWidth/3), stretch=0)
ruleTree.heading("# 2", text="Behavior")
ruleTree.column("# 3", anchor=CENTER, width=int(ruleTreeWidth/3), stretch=0)
ruleTree.heading("# 3", text="Date Added")

for i in range (len(rules[0])):
    textBehavior = "Mute on Lost Focus"
    if (bool(rules[1][i])):
        textBehavior = "Mute on Enter Focus"
    ruleTree.insert('', 'end', text=str(i+1), values=(rules[0][i], textBehavior, rules[2][i]))
ruleTree.configure(height=4)
ruleTree.place(x=75,y=500)

# Edit rule button
editButton = createImageButton(root, "Images/edit.png", (40,40), bCommand=edit)
editButton.place(x=930, y=530)

# Delete rule button
deleteButton = createImageButton(root, "Images/delete.png", (40,40), bCommand=delete)
deleteButton.place(x=930, y=575)

root.mainloop()