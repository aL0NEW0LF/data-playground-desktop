'''
NOTE: This alpha version of the app is not meant to be used in production. It is only meant to be used for testing purposes, and making sure that the app is working as intended. So the development is done to make a
specific workflow work.
'''
import tkinter as tk
from tkinter import ttk
import os
from webbrowser import get
import customtkinter as ctk
from PIL import ImageTk, Image
import pandas as pd
from pyparsing import col
from logic.file_handling import file_handling as fh
from pandastable import Table, TableModel
from tksheet import Sheet
from logic.data_preprocessing import feature_selection_kBestFeatures, feature_selection_varianceThreshold, handle_missing_values, drop_duplicate_rows, drop_contant_columns, get_non_constant_columns, get_constant_columns, remove_outliers
from enums import enums

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
            DATA.file_data_read()
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

def get_dataframe_columns():
    global DATA
    
    return DATA.file_data.columns.values.tolist()

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


        for F in (StartPage, RegressionPage, DecisionTreePage, NaiveBayesPage, SVMPage, KmeansPage, KNNPage, VarianceThresholdPage, KbestfeatPage, MissingValuesPage, DuplicateRowsPage, ConstantFeaturesPage, OutliersPage, RemoveColumnsPage):
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

        continueImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").rotate(180).resize((24, 24), Image.LANCZOS))

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        label = ctk.CTkLabel(self, text="Regression Page", text_color="#FFFFFF", font=LARGEFONT, bg_color="#101010", fg_color="#101010")
        label.grid(row=0, column=0, columnspan=5, padx=12, pady=12, sticky="nw")

        frame1 = ctk.CTkFrame(self, fg_color="#101010")
        frame1.grid(row=1, column=0, columnspan=5, ipadx=8, ipady=8, sticky="ew")

        button2 = ctk.CTkButton(frame1, image=backImg, text="", command=lambda: controller.show_frame(StartPage))
        button2.grid(row=0, column=0, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        button4 = ctk.CTkButton(frame1, text="Upload your data", command=lambda: self.upload_data())
        button4.grid(row=0, column=1, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        button1 = ctk.CTkButton(frame1, text="Print", command=lambda: print(DATA))
        button1.grid(row=0, column=2, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        optionmenu_var = ctk.StringVar(value="Features selection")
        combobox = ctk.CTkOptionMenu(master=frame1,
                                       values=["Variance threshold", "K-best features"],
                                       command=lambda x: self.optionmenu_callback(x, controller),
                                       variable=optionmenu_var,
                                       width=150)
        combobox.grid(row=0, column=3, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        optionmenu_var2 = ctk.StringVar(value="Preprocessing")
        combobox2 = ctk.CTkOptionMenu(master=frame1,
                                       values=["Missing values", "Duplicate rows", "Constant features", "Outliers", "Remove columns"],
                                       command=lambda x: self.optionmenu_callback(x, controller),
                                       variable=optionmenu_var2,
                                       width=150)
        combobox2.grid(row=0, column=4, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        button5 = ctk.CTkButton(frame1, image=continueImg, text="", command=lambda: controller.show_frame(KNNPage))
        button5.grid(row=0, column=5, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        frame2 = ctk.CTkFrame(self, fg_color="#101010")
        #frame2.configure(fg_color="#101010")
        frame2.grid(row=2, column=0, columnspan=5, ipadx=8, ipady=8, sticky="nsew")
        self.sheet = Sheet(frame2, data = None)
        self.sheet.enable_bindings()
        self.sheet.pack(side="top" , fill="both", expand=True)

    def upload_data(self):
        UploadAction()
        self.load_data()

    def load_data(self):
        global app
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
            controller.show_frame(KbestfeatPage)
        elif choice == "Missing values":
            app.frames[MissingValuesPage].textbox.configure(text = f"Number of missing values: {DATA.file_data.isnull().sum().sum()}\n\nPourcentage of missing values: {(DATA.file_data.isnull().sum().sum() / (DATA.file_data.shape[0] * DATA.file_data.shape[1])) * 100}%")
            controller.show_frame(MissingValuesPage)
        elif choice == "Duplicate rows":
            app.frames[DuplicateRowsPage].textbox.configure(text = f"Number of duplicate rows: {DATA.file_data.duplicated().sum()}\n\nPourcentage of duplicate rows: {(DATA.file_data.duplicated().sum() / DATA.file_data.shape[0]) * 100}%")
            controller.show_frame(DuplicateRowsPage)
        elif choice == "Constant features":
            app.frames[ConstantFeaturesPage].textbox.configure(text = f"Number of constant columns: {len(get_constant_columns(DATA.file_data))}\n\nPourcentage of constant columns: {(len(get_constant_columns(DATA.file_data)) / DATA.file_data.shape[1]) * 100}%")
            controller.show_frame(ConstantFeaturesPage)
        elif choice == "Outliers":
            controller.show_frame(OutliersPage)
        elif choice == "Remove columns":
            app.frames[RemoveColumnsPage].load_checkboxes()
            controller.show_frame(RemoveColumnsPage)

# FILLER PAGES ############################################################################################################################
###########################################################################################################################################
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

###########################################################################################################################################
###########################################################################################################################################
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

        button2 = ctk.CTkButton(self, text="Select features", command=lambda: self.kbestFeat_Selec_event(K_entry.get(), controller))
        button2.grid(row=3, column=0, padx=8, pady=8)

    def kbestFeat_Selec_event(self, k, controller):  
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

        for type in DATA.file_data.dtypes:
            if type == 'int64' and type == 'float64' and type == 'int32' and type == 'float32': 
                tk.messagebox.showerror("Information", "Please make sure all the features are numerical")
                return
        
        DATA.file_data = feature_selection_kBestFeatures(DATA.file_data.values, k)
        
        global app

        app.frames[RegressionPage].load_data()

        controller.show_frame(RegressionPage)

class MissingValuesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)

        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((32, 32), Image.LANCZOS))

        self.rowconfigure(2, weight=1)
        
        label = ctk.CTkLabel(self, text="MissingValuesPage", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        button1 = ctk.CTkButton(self, image=backImg, text="", width=32, height=32, command=lambda: controller.show_frame(RegressionPage))
        button1.grid(row=1, column=0, padx=8, pady=8, sticky="w")

        self.textbox = ctk.CTkLabel(self, text="", text_color="#FFFFFF", font=LARGEFONT)
        self.textbox.grid(row=2, column=0, sticky="nsew", columnspan=3)

        button4 = ctk.CTkButton(self, text="Fill with the mean", command=lambda: self.values_handling(method=enums.FillMethod.MEAN))
        button4.grid(row=3, column=0, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        button5 = ctk.CTkButton(self, text="Fill with the median", command=lambda: self.values_handling(method=enums.FillMethod.MEDIAN))
        button5.grid(row=3, column=1, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        button3 = ctk.CTkButton(self, text="Remove rows with missing values", command=lambda: self.values_handling(method=enums.FillMethod.DROP))
        button3.grid(row=3, column=2, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

    def values_handling(self, value: int | float | str = None, method: enums.FillMethod = enums.FillMethod.MEAN):
        global DATA

        handle_missing_values(DATA.file_data, value, method)

        self.textbox.configure(text = f"Number of missing values: {DATA.file_data.isnull().sum().sum()}\n\nPourcentage of missing values: {(DATA.file_data.isnull().sum().sum() / (DATA.file_data.shape[0] * DATA.file_data.shape[1])) * 100}%")
        
        global app
        app.frames[RegressionPage].load_data()
    

class DuplicateRowsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((32, 32), Image.LANCZOS))

        self.rowconfigure(2, weight=1)

        label = ctk.CTkLabel(self, text="DuplicateRowsPage", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10)

        button1 = ctk.CTkButton(self, image=backImg, text="", width=32, height=32, command=lambda: controller.show_frame(RegressionPage))
        button1.grid(row=1, column=0, padx=8, pady=8, sticky="w")

        self.textbox = ctk.CTkLabel(self, text="", text_color="#FFFFFF", font=LARGEFONT)
        self.textbox.grid(row=2, column=0, sticky="nsew", columnspan=3)

        button4 = ctk.CTkButton(self, text="Drop duplicate rows", command=lambda: self.drop_duplicate_rows())
        button4.grid(row=3, column=0, padx=0, pady=8, ipadx=8, ipady=8, sticky="w")

    def drop_duplicate_rows(self):
        global DATA

        drop_duplicate_rows(DATA.file_data)
        
        self.textbox.configure(text = f"Number of duplicate rows: {DATA.file_data.duplicated().sum()}\n\nPourcentage of duplicate rows: {(DATA.file_data.duplicated().sum() / DATA.file_data.shape[0]) * 100}%")
        
        global app
        app.frames[RegressionPage].load_data()


class ConstantFeaturesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((32, 32), Image.LANCZOS))

        label = ctk.CTkLabel(self, text="ConstantFeaturesPage", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10)

        button1 = ctk.CTkButton(self, image=backImg, text="", width=32, height=32, command=lambda: controller.show_frame(RegressionPage))
        button1.grid(row=1, column=0, padx=8, pady=8)

        self.textbox = ctk.CTkLabel(self, text="", text_color="#FFFFFF", font=LARGEFONT)
        self.textbox.grid(row=2, column=0, sticky="nsew", columnspan=3)

        button4 = ctk.CTkButton(self, text="Drop constant columns", command=lambda: self.drop_contant_columns())
        button4.grid(row=3, column=0, padx=0, pady=8, ipadx=8, ipady=8, sticky="w")

    def drop_contant_columns(self):
        global DATA
        
        DATA.file_data = DATA.file_data[get_non_constant_columns(DATA.file_data)]
        
        self.textbox.configure(text = f"Number of constant columns: {len(get_constant_columns(DATA.file_data))}\n\nPourcentage of constant columns: {(len(get_constant_columns(DATA.file_data)) / DATA.file_data.shape[1]) * 100}%")
        
        global app
        app.frames[RegressionPage].load_data()


class OutliersPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((32, 32), Image.LANCZOS))

        label = ctk.CTkLabel(self, text="OutliersPage", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10)

        button1 = ctk.CTkButton(self, image=backImg, text="", width=32, height=32, command=lambda: controller.show_frame(RegressionPage))
        button1.grid(row=1, column=0, padx=8, pady=8)

        button4 = ctk.CTkButton(self, text="Drop outliers based on z-score", command=lambda: self.outliers_handling(controller))
        button4.grid(row=2, column=0, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        button5 = ctk.CTkButton(self, text="Drop outliers based on percentiles", command=lambda: self.outliers_handling(controller, method=enums.OutlierMethod.IQR))
        button5.grid(row=2, column=1, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        
    def outliers_handling(self, controller, method: enums.OutlierMethod = enums.OutlierMethod.ZSCORE):
        global DATA

        remove_outliers(DATA.file_data, method)

        global app
        app.frames[RegressionPage].load_data()
        controller.show_frame(RegressionPage)


class RemoveColumnsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)

        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((32, 32), Image.LANCZOS))

        label = ctk.CTkLabel(self, text="OutliersPage", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10)

        button1 = ctk.CTkButton(self, image=backImg, text="", width=32, height=32, command=lambda: controller.show_frame(RegressionPage))
        button1.grid(row=1, column=0, padx=8, pady=8)

        button4 = ctk.CTkButton(self, text="Remove columns", command=lambda: self.remove_columns(controller))
        button4.grid(row=1, column=2, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")
        
        self.frame1 = ctk.CTkFrame(self, fg_color="#101010")
        self.frame1.grid(row=2, column=0, columnspan=5, ipadx=8, ipady=8, sticky="ew")
        
    def load_checkboxes(self):
        self.df_columns = get_dataframe_columns()

        """ self.l = Checkbar(self.frame1, self.df_columns)
        self.l.pack(anchor = 'w') """

        """ for x in range(len(self.df_columns)):
            self.l = ctk.CTkCheckBox(self.frame1, text=self.df_columns[x][0], variable=self.df_columns[x],command=lambda x=self.df_columns[x]:self.selected_df_columns.append(x), onvalue="on", offvalue="off")
            self.l.pack(anchor = 'w') """
        
        self.checkbuttons_vars = [tk.BooleanVar() for value in self.df_columns]
        
        self.checkbuttons = []
        for index, value in enumerate(self.df_columns):
            self.checkbutton = ctk.CTkCheckBox(self.frame1, text=value, variable=self.checkbuttons_vars[index], text_color="#FFFFFF")
            self.checkbutton.pack(side="top", anchor="w")
            self.checkbuttons.append(self.checkbutton)
    

    def remove_columns(self, controller):
        global DATA
        
        self.selected_values = [value for value, var in zip(self.df_columns, self.checkbuttons_vars) if var.get()]

        if len(self.selected_values) == 0:
            controller.show_frame(RegressionPage)
            for checkbutton in self.checkbuttons:
                checkbutton.destroy()
            self.checkbuttons.clear()
            return

        DATA.file_data.drop(self.selected_values, axis=1, inplace=True)

        global app
        app.frames[RegressionPage].load_data()
        controller.show_frame(RegressionPage)
        for checkbutton in self.checkbuttons:
            checkbutton.destroy()
        self.checkbuttons.clear()
   
   
# DRIVER CODE
app = App()
app.mainloop()
