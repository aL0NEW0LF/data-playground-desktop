import tkinter as tk
from tkinter import ttk
import os
import customtkinter as ctk
from PIL import ImageTk, Image
import pandas as pd
from logic.file_handling import file_handling as fh
from pandastable import Table, TableModel
from tksheet import Sheet
from logic.data_preprocessing import feature_selection_kBestFeatures, feature_selection_varianceThreshold

LARGEFONT = ("montserrat", 24)

# WRAPPER FUNCTIONS
def UploadAction():
    file_path = ctk.filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("JSON files", "*.json"), ("Text files", "*.txt")])
    print('Selected:', file_path)
    if not file_path:
        return
    _, file_extension = os.path.splitext(file_path)

    try:
        if file_extension in ['.csv', '.xlsx', '.json', '.txt']:
            global DATA
            DATA = fh(file_path=file_path, file_extension=file_extension)
            print(DATA)
        return

    except ValueError:
        ctk.messagebox.showerror("Information", "The file you have chosen is invalid")
        return
    except FileNotFoundError:
        ctk.messagebox.showerror("Information", f"No such file as {file_path}")
        return

def read_data():
    global DATA
    DATA.file_data_read()
    print(DATA)

def kbestFeat_Selec_event():
    dialog = ctk.CTkInputDialog(text="Type in a number:", title="Test")
    print("Number:", dialog.get_input())


# MAIN APP
class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        ctk.CTk.__init__(self, *args, **kwargs)

        self.geometry("1380x720")
        self.iconbitmap('./assets/icons/machine-learning.ico')
        self.title("Data playground")
        self.minsize(1380, 720)
        self.configure(fg_color="#161616")

        container = ctk.CTkFrame(self, width=self.winfo_width(), height=self.winfo_height())
        container.configure(fg_color="#101010")
        container.pack(side="bottom", expand=True, fill="both", padx=24, pady=24)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}


        for F in (StartPage, RegressionPage, DecisionTreePage, NaiveBayesPage, SVMPage, KmeansPage, KNNPage, VarianceThresholdPage, KbestfeatPage):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

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

        """ frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure((2, 0), weight=1) """


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
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        label = ctk.CTkLabel(self, text="Regression Page", text_color="#FFFFFF", font=LARGEFONT, bg_color="#101010", fg_color="#101010")
        label.grid(row=0, column=0, columnspan=5, padx=12, pady=12, sticky="nw")

        frame1 = ctk.CTkFrame(self, fg_color="#101010")
        frame1.grid(row=1, column=0, columnspan=5, ipadx=8, ipady=8, sticky="ew")

        button2 = ctk.CTkButton(frame1, image=backImg, text="", command=lambda: controller.show_frame(StartPage))
        button2.grid(row=0, column=0, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        button = ctk.CTkButton(frame1, text="Upload your data file", command= UploadAction)
        button.grid(row=0, column=1, padx=(0, 4), pady=8, ipadx=8, ipady=8, sticky="w")
        
        button3 = ctk.CTkButton(frame1, text="Read data file", command= read_data)
        button3.grid(row=0, column=2, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        button1 = ctk.CTkButton(frame1, text="Print", command=lambda: print(DATA))
        button1.grid(row=0, column=3, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        button4 = ctk.CTkButton(frame1, text="Load table", command=lambda: self.load_data())
        button4.grid(row=0, column=4, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        optionmenu_var = ctk.StringVar(value="")
        combobox = ctk.CTkOptionMenu(master=frame1,
                                       values=["Variance threshold", "K-best features"],
                                       command=lambda x: self.optionmenu_callback(x, controller),
                                       variable=optionmenu_var,
                                       width=150)
        combobox.grid(row=0, column=5, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        frame2 = ctk.CTkFrame(self, fg_color="#101010")
        #frame2.configure(fg_color="#101010")
        frame2.grid(row=2, column=0, columnspan=5, ipadx=8, ipady=8, sticky="nsew")
        self.sheet = Sheet(frame2, data = None)
        self.sheet.enable_bindings()
        self.sheet.pack(side="top" , fill="both", expand=True)

    def load_data(self):
        global DATA
        self.sheet.set_sheet_data(data = DATA.file_data.values.tolist())

        """ if self.sheet is None:
            self.sheet = Sheet(self.frame2, data = DATA.file_data.values.tolist())
            self.sheet.enable_bindings()
            self.sheet.pack(side="top" , fill="both", expand=True)
        else:
            self.sheet.set_sheet_data(data = DATA.file_data.values.tolist()) """
 
    def optionmenu_callback(self, choice, controller):
        if 'DATA' not in globals() or DATA.file_data is None:
            tk.messagebox.showerror("Information", "Please upload a data file first")
            return
        
        if choice == "Variance threshold":
            controller.show_frame(VarianceThresholdPage)
        elif choice == "K-best features":
            # kbestFeat_Selec_event()
            controller.show_frame(KbestfeatPage)

class DecisionTreePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((32, 32), Image.LANCZOS))

        label = ctk.CTkLabel(self, text="DecisionTreePage", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10)

        button1 = ctk.CTkButton(self, image=backImg, text="", width=32, height=32, command=lambda: controller.show_frame(StartPage))
        button1.grid(row=1, column=0, padx=8, pady=8)


class NaiveBayesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((32, 32), Image.LANCZOS))

        label = ctk.CTkLabel(self, text="NaiveBayesPage", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10)

        button1 = ctk.CTkButton(self, image=backImg, text="", width=32, height=32, command=lambda: controller.show_frame(StartPage))
        button1.grid(row=1, column=0, padx=8, pady=8)


class SVMPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((32, 32), Image.LANCZOS))

        label = ctk.CTkLabel(self, text="SVMPage", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10)

        button1 = ctk.CTkButton(self, image=backImg, text="", width=32, height=32, command=lambda: controller.show_frame(StartPage))
        button1.grid(row=1, column=0, padx=8, pady=8)


class KmeansPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((32, 32), Image.LANCZOS))

        label = ctk.CTkLabel(self, text="KmeansPage", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10)

        button1 = ctk.CTkButton(self, image=backImg, text="", width=32, height=32, command=lambda: controller.show_frame(StartPage))
        button1.grid(row=1, column=0, padx=8, pady=8)


class KNNPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((32, 32), Image.LANCZOS))

        label = ctk.CTkLabel(self, text="KNNPage", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=8, pady=8)

        button1 = ctk.CTkButton(self, image=backImg, text="", width=32, height=32, command=lambda: controller.show_frame(StartPage))
        button1.grid(row=1, column=0, padx=8, pady=8)

class VarianceThresholdPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((32, 32), Image.LANCZOS))

        label = ctk.CTkLabel(self, text="VarianceThresholdPage", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10)

        button1 = ctk.CTkButton(self, image=backImg, text="", width=32, height=32, command=lambda: controller.show_frame(RegressionPage))
        button1.grid(row=1, column=0, padx=8, pady=8)

class KbestfeatPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((32, 32), Image.LANCZOS))

        label = ctk.CTkLabel(self, text="KbestfeatPage", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10)
        
        button1 = ctk.CTkButton(self, image=backImg, text="", width=32, height=32, command=lambda: controller.show_frame(RegressionPage))
        button1.grid(row=1, column=0, padx=8, pady=8)
        
        K_entry = ctk.CTkEntry(self, width=10)
        K_entry.grid(row=2, column=0, padx=8, pady=8)

        button2 = ctk.CTkButton(self, text="Select features", command=lambda: self.kbestFeat_Selec_event(K_entry.get()))
        button2.grid(row=3, column=0, padx=8, pady=8)

    def kbestFeat_Selec_event(self, k):  
        global DATA

        if k == "":
            tk.messagebox.showerror("Information", "Please enter a value for k")
            return
        
        try:
            k = int(k)
        except ValueError:
            tk.messagebox.showerror("Information", "Please enter a valid value for k")
            return
        
        if k <= 0:
            tk.messagebox.showerror("Value", "The value you chose for k is invalid")
            return
        elif k >= DATA.file_data.shape[1]:
            tk.messagebox.showerror("Value", "The value you chose for k cant be greater than the number of features")
            return
        
        DATA.file_data = feature_selection_kBestFeatures(DATA.file_data.values, k)
        
        global app

        app.frames[RegressionPage].load_data()


# Driver Code
app = App()
app.mainloop()
