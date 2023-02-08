# Scope v1.0 by DucksIncoming
# Version last edited 2/7/2023
# https://github.com/DucksIncoming/Scope

from tkinter import *
from tkinter import ttk, font, messagebox
from PIL import ImageTk, Image
from datetime import date
import webbrowser
import json
from win32 import win32gui
import win32process, psutil
import pystray
from pystray import MenuItem as item
from pycaw.pycaw import AudioUtilities
import time
import sys
import os

def updateStartup():
    with open("appdata.json") as rFile:
        data = json.load(rFile)
        startup = data["settings"]["startWithWindows"]
    fileData = (__file__).split("\\")
    user = fileData[2]
    filepath = "C:\\Users\\" + user + "\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
    if (startup):
        os.path.realpath(filepath)
        os.startfile(filepath)

def resetAudio():
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume = session.SimpleAudioVolume
        volume.SetMasterVolume(1, None)

def getFocusedWindow():
    try:
        pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
        return(psutil.Process(pid[-1]).name())
    except:
        pass

# Implementation for minimizing to tray taken from this thread: https://stackoverflow.com/questions/54835399/running-a-tkinter-window-and-pystray-icon-together
def quit_window(icon, item):
    global ending
    ending = True
    global continueTrayRules
    global stopAllRules
    continueTrayRules = False
    stopAllRules = True
    icon.stop()
    resetAudio()
    sys.exit()

def show_window(icon, item):
    global enabled
    global continueTrayRules
    continueTrayRules = False
    icon.stop()
    root.after(0,root.deiconify)
    enabled = not enabled # hacky ass workaround lol
    sliderToggle()

def withdraw_window():  
    root.withdraw()
    image = Image.open("ico.png")
    menu = (item('Show GUI', show_window), item('Toggle Scope', trayToggle), item('Quit', quit_window))
    icon = pystray.Icon("Scope", image, "Scope", menu)
    
    with open("appdata.json") as rFile:
        data = json.load(rFile)
        minimizeOnClose = data["settings"]["minimize"]

    if (minimizeOnClose):
        icon.run_detached()
        trayApplyRules()
    else:
        resetAudio()
        root.destroy()

def trayApplyRules():
    global continueTrayRules
    continueTrayRules = True
    while continueTrayRules:
        rulePrograms = []
        ruleBehavior = []

        with open("appdata.json") as rFile:
            data = json.load(rFile)
            enabled = data["settings"]["enabled"]
            for rule in data["rules"]:
                rulePrograms.append(rule)
                ruleBehavior.append(data["rules"][rule]["behavior"])

        if (not enabled):
            resetAudio()
        else:
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                volume = session.SimpleAudioVolume
                if session.Process:
                    processName = session.Process.name().lower()
                    if processName in rulePrograms and getFocusedWindow():
                        focused = (getFocusedWindow().lower() == processName)
                        i = rulePrograms.index(processName)
                        if (bool(ruleBehavior[i]) == focused):
                            volume.SetMasterVolume(0, None)
                        else:
                            volume.SetMasterVolume(1, None)
                    else:
                        volume.SetMasterVolume(1, None)
        time.sleep(0.2)

def applyRules():
    rulePrograms = []
    ruleBehavior = []

    with open("appdata.json") as rFile:
        data = json.load(rFile)
        enabled = data["settings"]["enabled"]
        for rule in data["rules"]:
            rulePrograms.append(rule)
            ruleBehavior.append(data["rules"][rule]["behavior"])

    if (not enabled):
        resetAudio()
    else:
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            volume = session.SimpleAudioVolume
            if session.Process:
                processName = session.Process.name().lower()
                if processName in rulePrograms and getFocusedWindow():
                    focused = (getFocusedWindow().lower() == processName)
                    i = rulePrograms.index(processName)
                    if (bool(ruleBehavior[i]) == focused):
                        volume.SetMasterVolume(0, None)
                    else:
                        volume.SetMasterVolume(1, None)
                else:
                    volume.SetMasterVolume(1, None)
    if (not ending):
        root.after(200, applyRules)
    else:
        resetAudio()
        sys.exit()
    
def getActivePrograms():
    global programs
    programs = []
    psutil.process_iter(attrs=None, ad_value=None)
    for proc in psutil.process_iter():
        try:
            # Get process name & pid from process object.
            processName = proc.name()
            if (not processName.lower() in programs):
                programs.append(processName.lower())
        except:
            pass
    programs.sort()
    return programs

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
    # Settings popup window setup
    global settingsPopup
    global startWithWindows
    global minimize
    settingsPopup = Toplevel(root, background="#1e1e1e")
    settingsPopup.geometry("400x200")
    settingsPopup.resizable(width=False, height=False)

    # Settings text label
    settingsTitle = Label(settingsPopup, text="Settings", font=("Roboto", 16), foreground="white", background="#1e1e1e", )
    settingsTitle.pack(pady=10)

    # Checkboxes
    startWithWindows = IntVar(settingsPopup)
    startWinCheckbox = Checkbutton(settingsPopup, variable=startWithWindows, command=startWithWinSelect, text="Start with Windows", font=("Roboto", 12), background="#1e1e1e", foreground="white", activebackground="#1e1e1e", activeforeground="white", selectcolor="black")
    minimize = IntVar(settingsPopup)
    minimizeCheckbox = Checkbutton(settingsPopup, variable=minimize, command=minimizeSelect, text="Minimize to Tray", font=("Roboto", 12), background="#1e1e1e", foreground="white", activebackground="#1e1e1e", activeforeground="white", selectcolor="black")

    with open("appdata.json") as rFile:
        data = json.load(rFile)
        startWithWindows.set(int(data["settings"]["startWithWindows"]))
        minimize.set(int(data["settings"]["minimize"]))
    
    if (bool(startWithWindows.get())):
        startWinCheckbox.select()
    if (bool(minimize.get())):
        minimizeCheckbox.select()

    startWinCheckbox.pack()
    minimizeCheckbox.pack()

    # Github Link
    link = Label(settingsPopup, text="Github Repo", fg="#CED5FF", cursor="hand2", background="#1e1e1e", font=("Roboto", 12))
    link.pack(pady=20)
    link.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/DucksIncoming/Scope"))
    f = font.Font(link, link.cget("font"))
    f.configure(underline=True)
    link.configure(font=f)

def minimizeSelect():
    global startWithWindows
    global minimize

    with open("appdata.json") as rFile:
        data = json.load(rFile)
        data["settings"]["minimize"] = bool(minimize.get())
    with open("appdata.json", "w") as f:
        json.dump(data, f, indent=4)

def startWithWinSelect():
    global startWithWindows
    global minimize

    with open("appdata.json") as rFile:
        data = json.load(rFile)
        data["settings"]["startWithWindows"] = bool(startWithWindows.get())
    with open("appdata.json", "w") as f:
        json.dump(data, f, indent=4)

    updateStartup()

def refreshRuleTree():
    ruleTree.delete(*ruleTree.get_children())
    rules = getActiveRules()
    for i in range (len(rules[0])):
        textBehavior = "Mute on Lost Focus"
        if (bool(rules[1][i])):
            textBehavior = "Mute on Enter Focus"
        ruleTree.insert('', 'end', text=str(i), values=(rules[0][i], textBehavior, rules[2][i]))

def addRule():
    with open("appdata.json") as rFile:
        data = json.load(rFile)
        tempData = data["rules"]
        if (selectedProgram.get() == "Select Program"):
            return
        tempData[selectedProgram.get()] = {"behavior": behavior.get(), "date": str(date.today())}
    with open("appdata.json", "w") as f:
        json.dump(data, f, indent=4)

    refreshRuleTree()

def getActiveRules():
    programList = []
    behaviors = []
    dates = []

    with open("appdata.json") as rFile:
        data = json.load(rFile)
        data = data["rules"]
        for rule in data:
            tempData = data[rule]
            programList.append(rule)
            behaviors.append(tempData["behavior"])
            dates.append(tempData["date"])
        return [programList, behaviors, dates]

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
            with open('appdata.json') as in_file:
                data = json.load(in_file)
                tempData = data["rules"]
                for element in tempData:
                    if (str(element) == currentItem["values"][0]):
                        del data["rules"][element]
                        break
                with open("appdata.json", "w") as f:
                    json.dump(data, f, indent=4)
            refreshRuleTree()
    except:
        pass

def trayToggle():
    global enabled
    enabled = not enabled

    with open("appdata.json") as rFile:
        data = json.load(rFile)
        tempData = data["settings"]
        tempData["enabled"] = enabled
    with open("appdata.json", "w") as f:
        json.dump(data, f, indent=4)

def sliderToggle():
    global enabled
    if (enabled):
        enabled = False
        img = createImage(root, "Images/slider_0.png", (220,80))
        sliderText.config(text="Disabled", foreground="#f78686")
        
    else:
        enabled = True
        img = createImage(root, "Images/slider_1.png", (220,80))
        sliderText.config(text="Enabled", foreground="#b6d7a8")
    sliderButton.config(image=img)
    sliderButton.image = img

    with open("appdata.json") as rFile:
        data = json.load(rFile)
        tempData = data["settings"]
        tempData["enabled"] = enabled
    with open("appdata.json", "w") as f:
        json.dump(data, f, indent=4)

def programSelect(*args):
    global programs
    programs = getActivePrograms()
    programList.configure(values=programs)

# Global variables
global startWithWindows
global minimize
global enabled

# Base window setup
root = Tk()
root.title("Scope")
root.iconphoto(True, PhotoImage(file="ico.png"))
root.resizable(width=False, height=False)
root.geometry("1050x700")
root["background"] = "#1e1e1e"
ending = False
#root.wm_attributes('-toolwindow', 'true')

# Style stuff
style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", rowheight=40, )

# Settings icon
settingsButton = createImageButton(root, "Images/settings.png", (50,50), settingsToggle)
settingsButton.place(x=10, y=10)

# Scope Title at top of page
scopeImage = createImageLabel(root, "Images/scopeTitle.png", (220,120))
scopeImage.pack(pady=2)

# Enabled/Disabled slider
with open("appdata.json") as rFile:
    data = json.load(rFile)
    enabled = data["settings"]["enabled"]
sliderImage = "Images/slider_0.png"
sliderText = "Disabled"
sliderColor = "#f78686"
if (enabled):
    sliderImage = "Images/slider_1.png"
    sliderText = "Enabled"
    sliderColor = "#b6d7a8"
sliderButton = createImageButton(root, sliderImage, (220, 80), sliderToggle)
sliderButton.pack()

# Enabled/disabled text
sliderText = Label(root, text=sliderText, font=("Roboto", 16), foreground=sliderColor, background="#1e1e1e")
sliderText.config(anchor="center")
sliderText.place(x=480,y=185)

# Add rule label text
addRuleText = Label(root, text="Add New Rule", font=("Roboto", 24), foreground="white", background="#1e1e1e")
addRuleText.pack(pady=20)

# Program label text
programLabel = Label(root, text="Program", font=("Roboto", 18), foreground="#CECECE", background="#1e1e1e")
programLabel.place(x=210, y=260)

# Program dropdown menu
programs = getActivePrograms()
selectedProgram = StringVar(root)
selectedProgram.set("Select Program")
programList = ttk.Combobox(root, values=programs, state="readonly", textvariable=selectedProgram)
selectedProgram.trace("w", programSelect)
programList.config(width=100)
programList.pack(pady=20)

# Behavior label text
behaviorLabel = Label(root, text="Behavior", font=("Roboto", 18), foreground="#CECECE", background="#1e1e1e")
behaviorLabel.place(x=210, y=335)

# Behavior radio button options
behavior = IntVar(root)
lostFocusSelector = Radiobutton(root, text="Mute on Lost Focus", value=0, variable=behavior, background="#1e1e1e", activebackground="#1e1e1e", foreground="white", activeforeground="white", selectcolor="black", font=("Roboto", 12), cursor="hand2")
enterFocusSelector = Radiobutton(root, text="Mute on Enter Focus", value=1, variable=behavior, background="#1e1e1e", activebackground="#1e1e1e", foreground="white", activeforeground="white", selectcolor="black", font=("Roboto", 12), cursor="hand2")
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

stopAllRules = False
applyRules()
root.protocol('WM_DELETE_WINDOW', withdraw_window)
root.mainloop()

with open("appdata.json") as rFile:
    data = json.load(rFile)
    minimizeOnClose = data["settings"]["minimize"]

if (minimizeOnClose):
    withdraw_window()
resetAudio()