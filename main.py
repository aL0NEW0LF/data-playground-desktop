import tkinter as tk
from tkinter import ttk
import os
import customtkinter as ctk
from PIL import ImageTk, Image
import pandas as pd
from logic.file_handling import file_handling as fh
from pandastable import Table, TableModel

LARGEFONT = ("montserrat", 24)

def UploadAction():
    file_path = ctk.filedialog.askopenfilename()
    print('Selected:', file_path)
    if not file_path:
        return
    _, file_extension = os.path.splitext(file_path)

    try:
        if file_extension in ['.csv', '.xlsx', '.json', '.txt']:
            global DATA
            DATA = fh(file_path=file_path, file_extension=file_extension)
            print(DATA)
        return None

    except ValueError:
        ctk.messagebox.showerror("Information", "The file you have chosen is invalid")
        return None
    except FileNotFoundError:
        ctk.messagebox.showerror("Information", f"No such file as {file_path}")
        return None
        
class App(ctk.CTk):
    # __init__ function for class cApp
    def __init__(self, *args, **kwargs):
        # __init__ function for class CTk
        ctk.CTk.__init__(self, *args, **kwargs)

        self.geometry("1380x720")
        self.iconbitmap('./assets/icons/machine-learning.ico')
        self.title("Data playground")
        self.minsize(1380, 720)
        self.configure(fg_color="#161616")

        # creating a container
        container = ctk.CTkFrame(self)
        container.configure(fg_color="#101010")
        container.pack(side="bottom", expand=True, fill="both", padx=12, pady=12)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # initializing frames to an empty array
        self.frames = {}

        # iterating through a tuple consisting
        # of the different page layouts
        for F in (StartPage, RegressionPage, DecisionTreePage, NaiveBayesPage, SVMPage, KmeansPage, KNNPage):
            frame = F(container, self)

            # initializing frame of that object from
            # startpage, page1, page2 respectively with
            # for loop
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    # to display the current frame passed as
    # parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.configure(fg_color="#101010")
        frame.tkraise()


# first window frame startpage
class StartPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)

        frame = ctk.CTkFrame(self)
        frame.configure(fg_color="#101010")
        frame.place(relx=0.5, rely=0.5, anchor="c")

        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure((2, 0), weight=1)


        RegressionButton = ctk.CTkButton(frame,
                                         text="Regression",
                                         height=70,
                                         width=400,
                                         corner_radius=0,
                                         fg_color="#FFFFFF",
                                         text_color="#000000",
                                         font=("montserrat", 24),
                                         hover_color="#F0F0F0",
                                         command=lambda: controller.show_frame(RegressionPage))
        RegressionButton.grid(row=0, column=0, padx=20, pady=20, sticky="se")

        DecisionTreeButton = ctk.CTkButton(frame,
                                           text="Decision Tree",
                                           height=70,
                                           width=400,
                                           corner_radius=0,
                                           fg_color="#FFFFFF",
                                           text_color="#000000",
                                           font=("montserrat", 24),
                                           hover_color="#F0F0F0",
                                           command=lambda: controller.show_frame(DecisionTreePage))
        DecisionTreeButton.grid(row=0, column=1, padx=20, pady=20, sticky="s")

        NaiveBayesButton = ctk.CTkButton(frame,
                                         text="Naive Bayes",
                                         height=70,
                                         width=400,
                                         corner_radius=0,
                                         fg_color="#FFFFFF",
                                         text_color="#000000",
                                         font=("montserrat", 24),
                                         hover_color="#F0F0F0",
                                         command=lambda: controller.show_frame(NaiveBayesPage))
        NaiveBayesButton.grid(row=0, column=2, padx=20, pady=20, sticky="sw")

        SVMButton = ctk.CTkButton(frame,
                                  text="Support Vector Machine (SVM)",
                                  height=70,
                                  width=400,
                                  corner_radius=0,
                                  fg_color="#FFFFFF",
                                  text_color="#000000",
                                  font=("montserrat", 24),
                                  hover_color="#F0F0F0",
                                  command=lambda: controller.show_frame(SVMPage))
        SVMButton.grid(row=1, column=0, padx=20, pady=20, sticky="ne")

        KmeansButton = ctk.CTkButton(frame,
                                     text="Kmeans",
                                     height=70,
                                     width=400,
                                     corner_radius=0,
                                     fg_color="#FFFFFF",
                                     text_color="#000000",
                                     font=("montserrat", 24),
                                     hover_color="#F0F0F0",
                                     command=lambda: controller.show_frame(KmeansPage))
        KmeansButton.grid(row=1, column=1, padx=20, pady=20, sticky="n")

        KNNButton = ctk.CTkButton(frame,
                                  text="K nearest neighbor (KNN)",
                                  height=70,
                                  width=400,
                                  corner_radius=0,
                                  fg_color="#FFFFFF",
                                  text_color="#000000",
                                  font=("montserrat", 24),
                                  hover_color="#F0F0F0",
                                  command=lambda: controller.show_frame(KNNPage))
        KNNButton.grid(row=1, column=2, padx=20, pady=20, sticky="nw")



class RegressionPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((24, 24), Image.LANCZOS))

        label = ctk.CTkLabel(self, text="RegressionPage", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10)

        button = ctk.CTkButton(self, text="Upload your data file", command=UploadAction)
        button.grid(row=1, column=0, padx=8, pady=8, ipadx=8, ipady=8)
        
        button1 = ctk.CTkButton(self, text="Print", command=lambda: print(DATA)) # Raises the error -> NameError: name 'DATA' is not defined (TO SOLVE)
        button1.grid(row=2, column=0, padx=8, pady=8, ipadx=8, ipady=8)

        button2 = ctk.CTkButton(self, image=backImg, text="", command=lambda: controller.show_frame(StartPage))
        button2.grid(row=3, column=0, padx=8, pady=8, ipadx=8, ipady=8)
"""         # Frame for TreeView
        frame1 = ctk.CTkFrame(self)
        frame1.place(height=250, width=500)


        ## Treeview Widget
        tv1 = ttk.Treeview(frame1)
        tv1.place(relheight=1, relwidth=1) # set the height and width of the widget to 100% of its container (frame1).

        treescrolly = tk.Scrollbar(frame1, orient="vertical", command=tv1.yview) # command means update the yaxis view of the widget
        treescrollx = tk.Scrollbar(frame1, orient="horizontal", command=tv1.xview) # command means update the xaxis view of the widget
        tv1.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set) # assign the scrollbars to the Treeview Widget
        treescrollx.pack(side="bottom", fill="x") # make the scrollbar fill the x axis of the Treeview widget
        treescrolly.pack(side="right", fill="y") # make the scrollbar fill the y axis of the Treeview widget

    def clear_data(tv):
        tv1.delete(*tv1.get_children())
        return None """
    
class DecisionTreePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((32, 32), Image.LANCZOS))

        label = ctk.CTkLabel(self, text="DecisionTreePage", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10)

        # button to show frame 2 with text
        # layout2
        button1 = ctk.CTkButton(self, image=backImg, text="", width=32, height=32, command=lambda: controller.show_frame(StartPage))

        # putting the button in its place
        # by using grid
        button1.grid(row=1, column=0, padx=8, pady=8)


class NaiveBayesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((32, 32), Image.LANCZOS))

        label = ctk.CTkLabel(self, text="NaiveBayesPage", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10)

        # button to show frame 2 with text
        # layout2
        button1 = ctk.CTkButton(self, image=backImg, text="", width=32, height=32, command=lambda: controller.show_frame(StartPage))

        # putting the button in its place
        # by using grid
        button1.grid(row=1, column=0, padx=8, pady=8)


class SVMPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((32, 32), Image.LANCZOS))

        label = ctk.CTkLabel(self, text="SVMPage", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10)

        # button to show frame 2 with text
        # layout2
        button1 = ctk.CTkButton(self, image=backImg, text="", width=32, height=32, command=lambda: controller.show_frame(StartPage))

        # putting the button in its place
        # by using grid
        button1.grid(row=1, column=0, padx=8, pady=8)


class KmeansPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((32, 32), Image.LANCZOS))

        label = ctk.CTkLabel(self, text="KmeansPage", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10)

        # button to show frame 2 with text
        # layout2
        button1 = ctk.CTkButton(self, image=backImg, text="", width=32, height=32, command=lambda: controller.show_frame(StartPage))

        # putting the button in its place
        # by using grid
        button1.grid(row=1, column=0, padx=8, pady=8)


class KNNPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((32, 32), Image.LANCZOS))

        label = ctk.CTkLabel(self, text="KNNPage", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=8, pady=8)

        # button to show frame 2 with text
        # layout2
        button1 = ctk.CTkButton(self, image=backImg, text="", width=32, height=32, command=lambda: controller.show_frame(StartPage))

        # putting the button in its place
        # by using grid
        button1.grid(row=1, column=0, padx=8, pady=8)


# Driver Code
app = App()
app.mainloop()
