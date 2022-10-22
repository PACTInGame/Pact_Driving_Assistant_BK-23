from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
import tkinter.font as tkFont
import webbrowser


def callback():
    webbrowser.open_new("https://www.lfs.net/forum/thread/92775-The-PACT-Driving-Assistant---DOWNLOAD")


root = Tk()
root.geometry("600x300")
root.resizable(width=False, height=False)
root.configure(background='#3B3D3C')
root.title("Install Guide")
toolstyle = ttk.Style()
toolstyle.theme_use("clam")  # "default", "alt" .....

toolstyle.configure('TButton',
                    background="#3B3D3C",
                    foreground="#FFF2E2",
                    borderwidth=1,
                    bordercolor="grey",
                    focuscolor="none",
                    font=("Arial", 12))
toolstyle.map('TButton',
              background=[("pressed", "white"),
                          ("active", "grey")],
              borderwidth=[("active", 1)],
              bordercolor=[("active", "black")],
              foreground=[("pressed", "black"),
                          ("active", "black")]
              )


def open_img(i):
    global panel
    global btn
    global comm2
    global btnback
    string = "data\page" + str(i) + ".png"
    img = Image.open(string)
    img = img.resize((300, 300), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    if i > 0:
        panel.destroy()
    panel = Label(root, image=img)
    panel.image = img
    btn.destroy()
    try:
        btnback.destroy()
    except:
        pass
    panel.pack(side="right")
    if i == 0:
        comm = page1
    elif i == 1:
        comm = page2
    elif i == 2:
        comm = page3
    elif i == 3:
        comm = page4
    elif i == 5:
        comm = page7
    elif i == 6:
        comm = page8
    elif i == 7:
        comm = page6
    elif i == 8:
        comm = page9
    elif i == 9:
        comm = page10
    elif i == 10:
        comm = page11
    if not i == 11 and not i == 4:
        btn = ttk.Button(root, text='Continue', command=comm)
        btn.place(x=220, y=270, anchor="center")
    if not i == 0 and not i == 4 and not i == 11:
        btnback = ttk.Button(root, text='Back', command=comm2)
        btnback.place(x=80, y=270, anchor="center")


def page1():
    global w, comm2, comm2_0, btnback
    w["text"] = "Make sure, that no instance of LFS is running.\n" \
                "Close LFS if it is still active. \n" \
                "If you have done so. Press 'continue.'"
    comm2 = restart

    open_img(1)


def page2():
    global w, comm2, comm2_0, btnback
    w["text"] = "First steps first. Let's configure outgauge!\n" \
                "Go to your LFS Folder (usually under C:) and \n" \
                "select the file: cfg.txt."
    comm2 = page1

    open_img(2)


def page3():
    global w, comm2, comm2_0, btnback
    w["text"] = "Open the file and scroll down to Outgauge.\n" \
                "IMPORTANT: DO NOT EDIT OUTSIM! EDIT OUTGAUGE!! \n" \
                "Change the values to match those on the right.\n" \
                "REMEMBER TO SAVE THE FILE!"
    comm2 = page2

    try:
        btn2.destroy()
        btn3.destroy()
        btn4.destroy()
    except:
        pass


    open_img(3)


def page4():
    global w, comm2, comm2_0
    global btn2
    global btn3
    global btn4
    global btn
    global btnback
    w["text"] = "Now return to the PACT Driving Assistant Folder.\n" \
                "What controller do you use?"
    comm2 = page3

    btnback.destroy()
    btn.destroy()
    btnback = ttk.Button(root, text='Back', command=comm2, width=5)
    btnback.place(x=40, y=274, anchor="center")

    btn2 = ttk.Button(root, text='Wheel', command=page5)
    btn2.pack(side="bottom", padx="100", anchor="w", pady=(0, 10))
    btn3 = ttk.Button(root, text='Mouse', command=page6)
    btn3.pack(side="bottom", padx="100", anchor="w", pady=(0, 10))
    btn4 = ttk.Button(root, text='Keyboard', command=page6)
    btn4.pack(side="bottom", padx="100", anchor="w", pady=(0, 10))


def page5():
    global w, comm2, comm2_0, btnback
    btn2.destroy()
    btn3.destroy()
    btn4.destroy()
    w["text"] = "Install Vjoy if you want the car to auto-brake.\n" \
                "This may take a few minutes. \n"
    comm2 = page4

    open_img(5)


def page6():
    global w, comm2, comm2_0, btnback
    btn2.destroy()
    btn3.destroy()
    btn4.destroy()
    w["text"] = "Select the file controls.txt."
    comm2 = page4

    open_img(6)


def page7():
    global w, comm2, comm2_0, btnback
    w["text"] = "Usually, Vjoy gets stuck at 100%\n" \
                "while installing. That's just a bug.\n" \
                "AFTER 1-5 MINS at 100%:\n" \
                "Force close the installation and restart your computer.\n" \
                "Vjoy will be successfully installed..\n(Restart is necessary!)"
    comm2 = page5


    open_img(7)


def page8():
    global w, comm2, comm2_0, btnback
    w["text"] = "Edit those to match your LFS settings.\n" \
                "Orange: ALL USERS;\n" \
                "Green: WHEEL USERS;\n" \
                "Blue: KEYBOARD USERS\n" \
                "Mouse users only need to configure the orange settings.\n" \
                "You can find the axis settings here:\nLFS -> Options -> Controls -> Axes/FF"
    comm2 = page6

    open_img(8)


def page9():
    global w, comm2, comm2_0, btnback
    w["text"] = "You can already change assistance-settings.\n" \
                "Open settings.txt and change them to your preferences.\n" \
                "YOU CAN DO THAT LATER IN-GAME AS WELL.\n"
    comm2 = page8

    open_img(9)


def page10():
    global w, comm2, comm2_0, btnback
    w["text"] = "Now open LFS.\n" \
                "Type /insim 29999 in the chat \n(that will always be mandatory\n" \
                "to establish a connection!)\n"
    comm2 = page9
    try:
        btn5.destroy()
        btn6.destroy()
        w2.destroy()
    except:
        pass
    open_img(10)


def page11():
    global w, w2, btn5, btn6, comm2, comm2_0, btnback
    w["text"] = "Start the PACT DRIVING ASSISTANT\n" \
                "LFS will display the following in the chat:\n" \
                "'InSim - TCP: pyinsim\n" \
                "InSim: version 7 requested - using 7'\n" \
                "Enjoy!"
    comm2 = page10
    btnback.destroy()
    open_img(11)
    btnback = ttk.Button(root, text='Back', command=comm2, width=5)
    btnback.place(x=50, y=260, anchor="center")
    w2 = Label(root, text="If you still have trouble, contact me via LFS Forum\n"
                          "LFS Forum Thread: THE PACT DRIVING ASSISTANT\n"
                          "CLICK HERE!", bg="#3B3D3C", fg="#FFF2E2")
    f = tkFont.Font(w2, w2.cget("font"))
    f.configure(underline=True)
    w2.configure(font=f)
    w2.place(x=150, y=210, anchor="center")
    w2.bind("<Button-1>", lambda e: callback())
    btn5 = ttk.Button(root, text='Quit', command=root.destroy, width=5)
    btn5.place(x=250, y=260, anchor="center")
    btn6 = ttk.Button(root, text='Restart Tutorial', command=restart)
    btn6.place(x=150, y=260, anchor="center")



def restart():
    global btn, w
    try:
        panel.destroy()
        w.destroy()
        w2.destroy()
        btn5.destroy()
        btn6.destroy()
    except:
        pass
    welcome_text = "Hello there, welcome to the setup-assistant of the \n" \
                   "PACT Driving Assistant V11.X\nLet's get started."

    w = Label(root, text=welcome_text, bg="#3B3D3C", fg="#FFF2E2")

    w.place(x=150, y=150, anchor="center")

    btn = Button(root, text='Continue', command=page2)
    btn.place()

    open_img(0)


btnback = ttk.Button(root, text='Back', command=restart)
btn = ttk.Button(root, text='Continue', command=page1)
comm2_0 = restart
comm2 = restart
restart()
root.mainloop()
