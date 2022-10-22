import tkinter as tk


def warning():
    root = tk.Tk()
    root.configure(background='white')
    root.overrideredirect(True)
    root.geometry("300x150+810+520")
    root.lift()
    root.wm_attributes("-topmost", True)
    root.wm_attributes("-disabled", True)
    root.wm_attributes("-transparentcolor", "white")
    root.attributes('-alpha', 0.7)
    string = "warning"
    root.image = tk.PhotoImage(file='data\\' + string + '.png')
    label = tk.Label(root, image=root.image, bg='white')
    label.pack()
    root.after(3000, lambda: root.destroy())
    root.mainloop()


