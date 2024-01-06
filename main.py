'''
NOTE: This alpha version of the app is not meant to be used in production. It is only meant to be used for testing purposes, and making sure that the app is working as intended. So the development is done to make a
specific workflow work.
'''
from curses.ascii import isdigit
from re import S
import tkinter as tk
from tkinter import ttk
import os
from turtle import st, width
from webbrowser import get
import customtkinter as ctk
from PIL import ImageTk, Image
import joblib
from matplotlib import pyplot as plt
from matplotlib.font_manager import get_font
from numpy import full, pad
import pandas as pd
from pyparsing import col
from sklearn.calibration import LabelEncoder
from sklearn.exceptions import NotFittedError
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn import metrics, svm
from sklearn.cluster import KMeans
from logic.file_handling import file_handling as fh
from pandastable import Table, TableModel
from tksheet import Sheet
from logic.data_preprocessing import feature_selection_kBestFeatures, feature_selection_varianceThreshold, handle_missing_values, drop_duplicate_rows, drop_contant_columns, get_non_constant_columns, get_constant_columns, remove_outliers
from enums import enums
import matplotlib
from typing import Protocol

matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)


LARGEFONT = ("montserrat", 24)
MEDIUMFONT = ("montserrat", 16)
SMALLFONT = ("montserrat", 12)

MLModels = {'Linear Regression': LinearRegression(), 'Decision Tree': DecisionTreeClassifier(), 'Naive Bayes': GaussianNB(), 'Support Vector Machine (SVM)': svm.SVC(), 'K-means': KMeans(), 'K-Nearest Neighbors (KNN)': KNeighborsClassifier(), 'Random Forest': RandomForestClassifier(), 'Logistic Regression': LogisticRegression()}
DATA = fh()

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

            DATA.file_path = file_path
            DATA.file_extension = file_extension

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

# UNUSED
def kbestFeat_Selec_event():
    dialog = ctk.CTkInputDialog(text="Type in a number:", title="Test")
    print("Number:", dialog.get_input())

def get_dataframe_columns():
    global DATA
    
    return DATA.file_data.columns.values.tolist()

def get_dataframe_features():
    global DATA
    
    return DATA.X.columns.values.tolist()

# MAIN APP
class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        ctk.CTk.__init__(self, *args, **kwargs)

        """ CloseImg = ImageTk.PhotoImage(Image.open("./assets/icons/close.png").resize((12, 12), Image.LANCZOS))
        MinimizeImg = ImageTk.PhotoImage(Image.open("./assets/icons/minimize.png").resize((12, 12), Image.LANCZOS))
        self.FullscreenImg = ImageTk.PhotoImage(Image.open("./assets/icons/fullscreen.png").resize((12, 12), Image.LANCZOS))
        self.MinscreenImg = ImageTk.PhotoImage(Image.open("./assets/icons/minscreen.png").resize((12, 12), Image.LANCZOS)) """
        self.geometry("1380x720")
        self.iconbitmap('./assets/icons/machine-learning.ico')
        self.title("Data playground")
        self.minsize(1380, 720)
        self.configure(fg_color="#161616")
        """ self.wm_attributes('-type', 'splash')
        self.overrideredirect(True)
        
        title_bar = ctk.CTkFrame(self, width=self.winfo_width(), height=32,corner_radius=0)
        title_bar.configure(fg_color="#101010")
        title_bar.pack(side="top", fill="x")

        ButtonsFrame = ctk.CTkFrame(title_bar, height=32,corner_radius=0)
        ButtonsFrame.configure(fg_color="#101010")
        ButtonsFrame.pack(side="right", padx=0, pady=0)

        minimizeBtn = ctk.CTkButton(ButtonsFrame, text="", image=MinimizeImg, command=lambda: self.Iconify(), corner_radius=0, text_color="#FFFFFF", bg_color="#101010", fg_color="#101010", font=SMALLFONT, hover_color="#3d3d3d", height=32, width=40)
        minimizeBtn.grid(row=0, column=0, padx=0, pady=0, sticky="e")

        self.fullscreenBtn = ctk.CTkButton(ButtonsFrame, text="", image=self.FullscreenImg, command=lambda: self.maximize(), corner_radius=0, text_color="#FFFFFF", bg_color="#101010", fg_color="#101010", font=SMALLFONT, hover_color="#3d3d3d", height=32, width=40)
        self.fullscreenBtn.grid(row=0, column=1, padx=0, pady=0, sticky="e")

        closeBtn = ctk.CTkButton(ButtonsFrame, text="", image=CloseImg, command=lambda: self.destroy(), corner_radius=0, text_color="#FFFFFF", bg_color="#101010", fg_color="#101010", font=SMALLFONT, hover_color="#ff5757", height=32, width=40)
        closeBtn.grid(row=0, column=2, padx=0, pady=0, sticky="e") """

        container = ctk.CTkFrame(self, width=self.winfo_width(), height=self.winfo_height())
        container.configure(fg_color="#101010")
        container.pack(side="bottom", expand=True, fill="both", padx=24, pady=24)

        container.grid_rowconfigure(0, weight=1) 
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, DataProcessingPage, VisualizationPage, RemoveColumnsPage, DataSplitPage, MLPage):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.configure(fg_color="#101010")
        frame.tkraise()

    """ def maximize(self):
        self.wm_state('zoomed')
        self.fullscreenBtn.configure(image=self.MinscreenImg, command=lambda: self.minimize())

    def minimize(self):
        self.wm_state('normal')
        self.fullscreenBtn.configure(image=self.FullscreenImg, command=lambda: self.maximize())

    def Iconify(self):
        self.update_idletasks()
        self.overrideredirect(False)
        self.wm_state('iconic') """
    
# first window frame startpage
class StartPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)

        frame = ctk.CTkFrame(self)
        frame.configure(fg_color="#101010")
        frame.place(relx=0.5, rely=0.5, anchor="c")

        """ frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure((2, 0), weight=1) """


        UploadButton = ctk.CTkButton(frame,
                                         text="Upload your dataset",
                                         height=70,
                                         width=400,
                                         corner_radius=0,
                                         fg_color="#FFFFFF",
                                         text_color="#000000",
                                         font=LARGEFONT,
                                         hover_color="#F0F0F0")
        UploadButton.configure(command=lambda: self.upload_data(controller))
        UploadButton.grid(row=0, column=0, padx=20, pady=20, sticky="se")

    def button_click_controller(self, btn: ctk.CTkButton, controller):
        # self.mlModel = MLModels[btn.cget('text')]
        global DATA 

        DATA.mlModelType = btn.cget('text')
        DATA.mlModel = MLModels[DATA.mlModelType]
        print(DATA.mlModelType)
        controller.show_frame(DataProcessingPage)

    def upload_data(self, controller):
        UploadAction()
        app.frames[DataProcessingPage].load_data()

        app.frames[DataProcessingPage].combobox1.configure(values=get_dataframe_columns())

        app.frames[DataProcessingPage].combobox1.configure(state='normal')
        app.frames[DataProcessingPage].combobox.configure(state='disabled')
        app.frames[DataProcessingPage].combobox2.configure(state='disabled')
        app.frames[DataProcessingPage].button6.configure(state='disabled')
        app.frames[DataProcessingPage].button5.configure(state='disabled')

        controller.show_frame(DataProcessingPage)

class DataProcessingPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((24, 24), Image.LANCZOS))

        continueImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").rotate(180).resize((24, 24), Image.LANCZOS))

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        label = ctk.CTkLabel(self, text="Data processing", text_color="#FFFFFF", font=LARGEFONT, bg_color="#101010", fg_color="#101010")
        label.grid(row=0, column=0, columnspan=5, padx=0, pady=8, sticky="nw")

        frame1 = ctk.CTkFrame(self, fg_color="#101010")
        frame1.grid(row=1, column=0, sticky="ew")

        self.button4 = ctk.CTkButton(frame1, text="Upload your data", command=lambda: self.upload_data(), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48)
        self.button4.grid(row=0, column=0, padx=(0, 4), pady=8, sticky="w")

        self.optionmenu_var2 = ctk.StringVar(value="Target column")
        self.combobox1 = ctk.CTkOptionMenu(master=frame1,
                                       values=[],
                                       variable=self.optionmenu_var2, 
                                       state='disabled',
                                       command=lambda x: self.split_X_y(x), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=48, width=146, button_color="#FFFFFF", button_hover_color="#FFFFFF", dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF")
        self.combobox1.grid(row=0, column=1, padx=4, pady=8, sticky="w")

        self.button6 = ctk.CTkButton(frame1, text="Visualize", command=lambda: self.VisPageSwitch(controller=controller), state='disabled', corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48)
        self.button6.grid(row=0, column=2, padx=4, pady=8, sticky="w")

        self.button7 = ctk.CTkButton(frame1, text="Save dataset", command=lambda: self.show_frame(SaveDatasetPage), state='disabled', corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48)
        self.button7.grid(row=0, column=3, padx=4, pady=8, sticky="w")

        self.button5 = ctk.CTkButton(frame1, image=continueImg, text="", command=lambda: self.SplitPageSwitch(controller), state='disabled', corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48, width=56)
        self.button5.grid(row=0, column=4, padx=4, pady=8, sticky="w")

        frame2 = ctk.CTkFrame(self, fg_color="#101010")
        #frame2.configure(fg_color="#101010")
        frame2.grid(row=2, column=0, columnspan=5, ipadx=8, ipady=8, sticky="nsew")

        frame2.rowconfigure(0, weight=1)
        frame2.columnconfigure(1, weight=1)

        frame3 = ctk.CTkFrame(frame2, fg_color="#101010", width=358)
        frame3.grid(row=0, column=0, padx=(0, 8), pady=0, ipadx=0, ipady=0, sticky="nw")
        frame3.rowconfigure(1, weight=1)

        frame5 = ctk.CTkFrame(frame3, fg_color="#101010", width=358)
        frame5.grid(row=0, column=0, padx=0, pady=0, ipadx=0, ipady=0, sticky="nw")

        separator = ttk.Separator(frame3, orient='horizontal')
        separator.grid(row=1, column=0, padx=0, pady=0, ipadx=0, ipady=0, sticky="ew")

        self.frame6 = ctk.CTkFrame(frame3, fg_color="#191919", width=358)
        self.frame6.grid(row=2, column=0, padx=0, pady=0, ipadx=0, ipady=0, sticky="nw")

        self.optionmenu_var = ctk.StringVar(value="Features selection")
        self.combobox = ctk.CTkOptionMenu(master=frame5,
                                       values=["Variance threshold", "K-best features"],
                                       command=lambda x: self.optionmenu_callback(x, controller),
                                       variable=self.optionmenu_var, 
                                       state='disabled', corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=48, width=175, button_color="#FFFFFF", button_hover_color="#FFFFFF", dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF")
        self.combobox.grid(row=0, column=0, padx=(0, 4), pady=(0, 8), sticky="w")

        self.optionmenu_var2 = ctk.StringVar(value="Preprocessing")
        self.combobox2 = ctk.CTkOptionMenu(master=frame5,
                                       values=["Missing values", "Duplicate rows", "Constant features", "Outliers", "Remove columns", "Label encoding"],
                                       command=lambda x: self.optionmenu_callback(x, controller),
                                       variable=self.optionmenu_var2, 
                                       state='disabled', corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=48, width=175, button_color="#FFFFFF", button_hover_color="#FFFFFF", dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF")
        self.combobox2.grid(row=0, column=1, padx=(4, 0), pady=(0, 8), sticky="w")

        frame4 = ctk.CTkFrame(frame2, fg_color="#101010")
        frame4.grid(row=0, column=1, ipadx=0, ipady=0, sticky="nsew")

        self.sheet = Sheet(frame4, data = None)
        self.sheet.enable_bindings()
        self.sheet.pack(side="top" , fill="both", expand=True)

        self.frames = {}

        for F in (VarianceThresholdPage, KbestfeatPage, MissingValuesPage, DuplicateRowsPage, ConstantFeaturesPage, OutliersPage, RemoveColumnsPage, LabelEncodingPage, SaveDatasetPage, BlankPage):
            frame = F(self.frame6, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(BlankPage)
        
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.configure(fg_color="#101010", width=358)
        frame.tkraise()
        """ self.frame6.winfo_children()[0].destroy()
        frame = cont(self.frame6, self)
        frame.grid(row=0, column=0, sticky="nsew") """

    def upload_data(self):
        UploadAction()
        self.load_data()

        self.combobox1.configure(values=get_dataframe_columns())

        self.combobox1.configure(state='normal')
        self.combobox.configure(state='disabled')
        self.combobox2.configure(state='disabled')
        self.button6.configure(state='disabled')
        self.button5.configure(state='disabled')

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
            self.show_frame(VarianceThresholdPage)
        elif choice == "K-best features":
            for type in DATA.file_data.dtypes.values:
                if type != 'int64' and type != 'float64' and type != 'int32' and type != 'float32': 
                    tk.messagebox.showerror("Information", "Please make sure all the features are numerical")
                    return
            self.show_frame(KbestfeatPage)
        elif choice == "Missing values":
            self.frames[MissingValuesPage].textbox.configure(text = f"Number of missing values: {DATA.file_data.isnull().sum().sum()}\n\nPourcentage of missing values: {round((DATA.file_data.isnull().sum().sum() / (DATA.file_data.shape[0] * DATA.file_data.shape[1])) * 100, 2)}%")
            self.show_frame(MissingValuesPage)
        elif choice == "Duplicate rows":
            self.frames[DuplicateRowsPage].textbox.configure(text = f"Number of duplicate rows: {DATA.file_data.duplicated().sum()}\n\nPourcentage of duplicate rows: {round((DATA.file_data.duplicated().sum() / DATA.file_data.shape[0]) * 100, 2)}%")
            self.show_frame(DuplicateRowsPage)
        elif choice == "Constant features":
            self.frames[ConstantFeaturesPage].textbox.configure(text = f"Number of constant columns: {len(get_constant_columns(DATA.file_data))}\n\nPourcentage of constant columns: {round((len(get_constant_columns(DATA.file_data)) / DATA.file_data.shape[1]) * 100, 2)}%")
            self.show_frame(ConstantFeaturesPage)
        elif choice == "Outliers":
            self.show_frame(OutliersPage)
        elif choice == "Remove columns":
            self.frames[RemoveColumnsPage].load_checkboxes()
            self.show_frame(RemoveColumnsPage)
        elif choice == "Label encoding":
            self.frames[LabelEncodingPage].combobox1.configure(values=get_dataframe_columns())
            self.show_frame(LabelEncodingPage)

    def VisPageSwitch(self, controller):
        if 'DATA' not in globals() or DATA.file_data is None:
            tk.messagebox.showerror("Information", "Please upload a data file first")
            return
        
        global app
        app.frames[VisualizationPage].combobox1.configure(values=get_dataframe_columns())
        app.frames[VisualizationPage].combobox2.configure(values=get_dataframe_columns())
        controller.show_frame(VisualizationPage)

    def SplitPageSwitch(self, controller):
        if 'DATA' not in globals() or DATA.file_data is None:
            tk.messagebox.showerror("Information", "Please upload a data file first")
            return
        elif 'object' in DATA.file_data.dtypes.to_dict().values(): 
            tk.messagebox.showerror("Information", "Please make sure all the labels are encoded")
            return
                
        self.show_frame(BlankPage)
        controller.show_frame(DataSplitPage)

    def split_X_y(self, choice: str):
        global DATA

        choice_type = DATA.file_data[choice].dtype.name

        if DATA.mlModelType == 'Linear Regression':
            if choice_type != 'int64' and choice_type != 'float64' and choice_type != 'int32' and choice_type != 'float32':
                tk.messagebox.showerror("Information", "Please choose a valid target column for linear regression")
                return
        else: 
            if choice_type == 'float64' or choice_type == 'float32':
                tk.messagebox.showerror("Information", "Please choose a valid target column for classification")
                return

        if choice is None or choice == "":
            tk.messagebox.showerror("Information", "Choose a target class")
            return

        DATA.target_column = choice

        print(DATA.target_column)

        DATA.X = DATA.file_data.drop(DATA.target_column, axis=1)
        DATA.y = DATA.file_data[DATA.target_column]

        DATA.file_data = pd.concat([DATA.X, DATA.y], axis=1)

        self.load_data()

        self.combobox.configure(state='normal')
        self.combobox2.configure(state='normal')
        self.button6.configure(state='normal')
        self.button5.configure(state='normal')
        self.button7.configure(state='normal')

# FILLER PAGES ############################################################################################################################
###########################################################################################################################################
class BlankPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.configure(fg_color="#101010", width=200)
###########################################################################################################################################
###########################################################################################################################################

class VarianceThresholdPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((24, 24), Image.LANCZOS))

        self.columnconfigure(0, weight=1)

        label = ctk.CTkLabel(self, text="Variance threshold", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=0, pady=8, sticky="w")
        
        frame1 = ctk.CTkFrame(self, fg_color="#101010")
        frame1.grid(row=1, column=0, ipadx=0, ipady=0, columnspan=3, sticky="ew")

        frame1.columnconfigure(1, weight=1)

        threshold_label = ctk.CTkLabel(frame1, text="Choose the variance threshold you want:", text_color="#FFFFFF", font=SMALLFONT)
        threshold_label.grid(row=0, column=0, padx=(0, 4), pady=8)

        threshold_entry = ctk.CTkEntry(frame1, width=100, corner_radius=0)
        threshold_entry.grid(row=0, column=1, padx=(4, 0), pady=8, sticky="ew")

        ApplyButton = ctk.CTkButton(self, text="Select features", command=lambda: self.apply_threshold(threshold_entry.get(), controller), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48)
        ApplyButton.grid(row=2, column=0, padx=0, pady=(8, 4), sticky="ew")

        CancelButton = ctk.CTkButton(self, image=backImg, text="", command=lambda: controller.show_frame(BlankPage), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48, width=56)
        CancelButton.grid(row=3, column=0, padx=0, pady=4, sticky="ew")

    def apply_threshold(self, k, controller):

        global DATA

        if k == "" or k is None:
            tk.messagebox.showerror("Information", "Please enter a value for the threshold")
            return
        
        try:
            k = float(k)
        except ValueError:
            tk.messagebox.showerror("Information", "Please enter a valid value for the threshold")
            return

        # print threshold
        print(f"Threshold value: {k}")

        DATA.file_data = feature_selection_varianceThreshold(DATA.file_data, k)
        print(f"New DataFrame shape: {DATA.file_data.shape}")

        global app
        app.frames[DataProcessingPage].load_data()

        print(f"Variance thresholding applied successfully. "
                                       f"Updated dataset shape: {DATA.file_data.shape}")
        
        controller.show_frame(BlankPage)


class KbestfeatPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.configure(fg_color="#101010", width=358)

        self.columnconfigure(0, weight=1)

        label = ctk.CTkLabel(self, text="K-best features", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        frame = ctk.CTkFrame(self, fg_color="#101010")
        frame.grid(row=1, column=0, ipadx=0, ipady=0, sticky="ew")
        
        frame.columnconfigure(1, weight=1)

        label = ctk.CTkLabel(frame, text="Number of features you want to keep\n(Less than the number of actual\nfeatures):", text_color="#FFFFFF", font=SMALLFONT)
        label.grid(row=0, column=0, padx=(0, 4), pady=8, sticky="w")

        K_entry = ctk.CTkEntry(frame, width=100, corner_radius=0)
        K_entry.grid(row=0, column=1, padx=(4, 0), pady=8, sticky="ew")
        
        button2 = ctk.CTkButton(self, text="Select features", command=lambda: self.kbestFeat_Selec_event(K_entry.get(), controller), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48)
        button2.grid(row=2, column=0, padx=0, pady=(8, 4), sticky="ew")

        button1 = ctk.CTkButton(self, text="Cancel", command=lambda: controller.show_frame(BlankPage), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48)
        button1.grid(row=3, column=0, padx=0, pady=4, sticky="ew")

    def kbestFeat_Selec_event(self, k, controller):  
        global DATA

        if k == "" or k is None:
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
        
        feature_selection_kBestFeatures(DATA.file_data, k)
        
        global app

        app.frames[DataProcessingPage].load_data()

        controller.show_frame(DataProcessingPage)

class MissingValuesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.configure(fg_color="#101010", width=358)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        label = ctk.CTkLabel(self, text="Missing values", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        self.textbox = ctk.CTkLabel(self, text="", text_color="#FFFFFF", font=SMALLFONT)
        self.textbox.grid(row=1, column=0, padx=0, pady=8, sticky="w")
        
        button4 = ctk.CTkButton(self, text="Fill with the mean", command=lambda: self.values_handling(method=enums.FillMethod.MEAN), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=32)
        button4.grid(row=2, column=0, padx=0, pady=(8, 4), ipadx=8, ipady=8, sticky="ew")

        button5 = ctk.CTkButton(self, text="Fill with the median", command=lambda: self.values_handling(method=enums.FillMethod.MEDIAN), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=32)
        button5.grid(row=3, column=0, padx=0, pady=4, ipadx=8, ipady=8, sticky="ew")

        button3 = ctk.CTkButton(self, text="Remove rows with missing values", command=lambda: self.values_handling(method=enums.FillMethod.DROP), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=32)
        button3.grid(row=4, column=0, padx=0, pady=4, ipadx=8, ipady=8, sticky="ew")

        button1 = ctk.CTkButton(self, text="Cancel", command=lambda: controller.show_frame(BlankPage), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48, width=56)
        button1.grid(row=5, column=0, padx=0, pady=4, sticky="ew")

    def values_handling(self, value: int | float | str = None, method: enums.FillMethod = enums.FillMethod.MEAN):
        global DATA

        handle_missing_values(DATA.file_data, value, method)
        
        DATA.X = DATA.file_data.drop(DATA.target_column, axis=1)
        DATA.y = DATA.file_data[DATA.target_column]
        
        self.textbox.configure(text = f"Number of missing values: {DATA.file_data.isnull().sum().sum()}\n\nPourcentage of missing values: {(DATA.file_data.isnull().sum().sum() / (DATA.file_data.shape[0] * DATA.file_data.shape[1])) * 100}%")
        
        global app
        app.frames[DataProcessingPage].load_data()
    

class DuplicateRowsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.configure(fg_color="#101010", width=358)
        self.columnconfigure(0, weight=1)

        label = ctk.CTkLabel(self, text="Duplicate Rows", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        self.textbox = ctk.CTkLabel(self, text="", text_color="#FFFFFF", font=SMALLFONT)
        self.textbox.grid(row=1, column=0, pady=8, sticky="w", columnspan=3)

        button4 = ctk.CTkButton(self, text="Drop duplicate rows", command=lambda: self.drop_duplicate_rows(), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=32)
        button4.grid(row=2, column=0, padx=0, pady=(8, 4), ipadx=8, ipady=8, sticky="ew")

        button1 = ctk.CTkButton(self, text="Cancel", command=lambda: controller.show_frame(BlankPage), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48)
        button1.grid(row=3, column=0, padx=0, pady=4, sticky="ew")

    def drop_duplicate_rows(self):
        global DATA

        drop_duplicate_rows(DATA.file_data)
        
        self.textbox.configure(text = f"Number of duplicate rows: {DATA.file_data.duplicated().sum()}\n\nPourcentage of duplicate rows: {(DATA.file_data.duplicated().sum() / DATA.file_data.shape[0]) * 100}%")
        
        global app
        app.frames[DataProcessingPage].load_data()


class ConstantFeaturesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.configure(fg_color="#101010", width=358)
        self.columnconfigure(0, weight=1)

        label = ctk.CTkLabel(self, text="Constant features", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        self.textbox = ctk.CTkLabel(self, text="", text_color="#FFFFFF", font=SMALLFONT)
        self.textbox.grid(row=1, column=0, pady=8, sticky="w")

        button4 = ctk.CTkButton(self, text="Drop constant columns", command=lambda: self.drop_contant_columns(), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=32)
        button4.grid(row=2, column=0, padx=0, pady=(8, 4), ipadx=8, ipady=8, sticky="ew")

        button1 = ctk.CTkButton(self, text="Cancel", command=lambda: controller.show_frame(BlankPage), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48)
        button1.grid(row=3, column=0, padx=0, pady=4, sticky="ew")

    def drop_contant_columns(self):
        global DATA
        
        DATA.file_data = DATA.file_data[get_non_constant_columns(DATA.file_data)]
        
        self.textbox.configure(text = f"Number of constant columns: {len(get_constant_columns(DATA.file_data))}\n\nPourcentage of constant columns: {(len(get_constant_columns(DATA.file_data)) / DATA.file_data.shape[1]) * 100}%")
        
        global app
        app.frames[DataProcessingPage].load_data()


class OutliersPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.configure(fg_color="#101010", width=358)
        self.columnconfigure(0, weight=1)

        label = ctk.CTkLabel(self, text="Outliers", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        button4 = ctk.CTkButton(self, text="Drop outliers based on z-score", command=lambda: self.outliers_handling(controller), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=32)
        button4.grid(row=1, column=0, padx=0, pady=(0, 4), ipadx=8, ipady=8, sticky="ew")

        button5 = ctk.CTkButton(self, text="Drop outliers based on percentiles", command=lambda: self.outliers_handling(controller, method=enums.OutlierMethod.IQR), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=32)
        button5.grid(row=2, column=0, padx=0, pady=4, ipadx=8, ipady=8, sticky="ew")

        button1 = ctk.CTkButton(self, text="Cancel", command=lambda: controller.show_frame(BlankPage), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48)
        button1.grid(row=3, column=0, padx=0, pady=4, sticky="ew")


    def outliers_handling(self, controller, method: enums.OutlierMethod = enums.OutlierMethod.ZSCORE):
        global DATA

        remove_outliers(DATA.file_data, method)

        global app
        app.frames[DataProcessingPage].load_data()
        controller.show_frame(BlankPage)


class RemoveColumnsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.configure(fg_color="#101010", width=358)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.checkbuttons_vars = []
        self.checkbuttons = []
        self.df_columns = []

        label = ctk.CTkLabel(self, text="Remove columns", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        self.frame1 = ctk.CTkScrollableFrame(self, fg_color="#101010")
        self.frame1.grid(row=1, column=0, ipadx=8, ipady=8, pady=8, sticky="ew")
        
        button4 = ctk.CTkButton(self, text="Remove columns", command=lambda: self.remove_columns(controller), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=32)
        button4.grid(row=2, column=0, padx=0, pady=(8, 4), ipadx=8, ipady=8, sticky="ew")

        button1 = ctk.CTkButton(self, text="Cancel", command=lambda: controller.show_frame(BlankPage), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48)
        button1.grid(row=3, column=0, padx=0, pady=4, sticky="ew")

    def load_checkboxes(self):
        self.df_columns = get_dataframe_features()

        """ self.l = Checkbar(self.frame1, self.df_columns)
        self.l.pack(anchor = 'w') """

        """ for x in range(len(self.df_columns)):
            self.l = ctk.CTkCheckBox(self.frame1, text=self.df_columns[x][0], variable=self.df_columns[x],command=lambda x=self.df_columns[x]:self.selected_df_columns.append(x), onvalue="on", offvalue="off")
            self.l.pack(anchor = 'w') """
        
        for checkbutton in self.frame1.winfo_children():
            checkbutton.destroy()

        self.checkbuttons_vars = [tk.BooleanVar() for value in self.df_columns]

        self.checkbuttons = []
        for index, value in enumerate(self.df_columns):
            self.checkbutton = ctk.CTkCheckBox(self.frame1, text=value, variable=self.checkbuttons_vars[index], text_color="#FFFFFF", corner_radius=0, font=SMALLFONT, border_color="#F0F0F0", hover_color="#F0F0F0", fg_color="#FFFFFF")
            self.checkbutton.pack(side="top", anchor="center", expand=True, fill="both", padx=0, pady=4)
            self.checkbuttons.append(self.checkbutton)

    def remove_columns(self, controller):
        global DATA
        
        self.selected_values = [value for value, var in zip(self.df_columns, self.checkbuttons_vars) if var.get()]

        DATA.file_data.drop(self.selected_values, axis=1, inplace=True)

        DATA.X = DATA.file_data.drop(DATA.target_column, axis=1)
        DATA.y = DATA.file_data[DATA.target_column]

        global app

        app.frames[DataProcessingPage].combobox1.configure(values=get_dataframe_columns())
        app.frames[DataProcessingPage].load_data()
        controller.show_frame(BlankPage)

        self.checkbuttons.clear()
        self.checkbuttons_vars.clear()
        self.df_columns.clear()

    def back_handler(self, controller):
        global app

        app.frames[DataProcessingPage].combobox1.configure(values=get_dataframe_columns())
        app.frames[DataProcessingPage].load_data()
        controller.show_frame(BlankPage)

        self.checkbuttons.clear()
        self.checkbuttons_vars.clear()
        self.df_columns.clear()

class LabelEncodingPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.configure(fg_color="#101010", width=358)
        self.columnconfigure(0, weight=1)

        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((24, 24), Image.LANCZOS))

        label = ctk.CTkLabel(self, text="Label encoding", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        self.optionmenu_var2 = ctk.StringVar(value="Column X")
        self.combobox1 = ctk.CTkOptionMenu(master=self,
                                       values=[],
                                       command=lambda x: self.Column_choice_handler(x, controller),
                                       variable=self.optionmenu_var2,
                                       width=150,
                                       corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=32, button_color="#FFFFFF", button_hover_color="#FFFFFF", dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF")
        self.combobox1.grid(row=1, column=0, padx=0, pady=(8, 4), ipadx=8, ipady=8, sticky="ew")

        button1 = ctk.CTkButton(self, text="Cancel", command=lambda: controller.show_frame(BlankPage), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48)
        button1.grid(row=2, column=0, padx=0, pady=4, sticky="ew")

    def Column_choice_handler(self, choice: str, controller):
        global app
        global DATA

        DATA.file_data[choice] = LabelEncoder().fit_transform(DATA.file_data[choice])

        DATA.X = DATA.file_data.drop(DATA.target_column, axis=1)
        DATA.y = DATA.file_data[DATA.target_column]

        app.frames[DataProcessingPage].load_data()
        controller.show_frame(BlankPage)

class VisualizationPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((24, 24), Image.LANCZOS))
        # prepare data
        self.visPlotType = None
        self.visColumnX = None
        self.visColumnY = None

        label = ctk.CTkLabel(self, text="Visualization", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        frame1 = ctk.CTkFrame(self, fg_color="#101010")
        frame1.grid(row=1, column=0, ipadx=0, ipady=0, columnspan=3, sticky="ew")

        button1 = ctk.CTkButton(frame1, image=backImg, text="", command=lambda: controller.show_frame(DataProcessingPage), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48, width=56)
        button1.grid(row=0, column=0, padx=(0, 4), pady=8, sticky="w")

        self.optionmenu_var = ctk.StringVar(value="Plot type")
        self.combobox = ctk.CTkOptionMenu(master=frame1,
                                       values=["Scatter plot", "Histogram", "Bar chart", "Line chart", "Box plot"],
                                       command=lambda x: self.plotType_optionmenu_callback(x),
                                       variable=self.optionmenu_var,
                                       width=150, corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=32, button_color="#FFFFFF", button_hover_color="#FFFFFF", dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF")
        self.combobox.grid(row=0, column=3, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        self.optionmenu_var2 = ctk.StringVar(value="Column X")
        self.combobox1 = ctk.CTkOptionMenu(master=frame1,
                                       values=[],
                                       command=lambda x: self.columnX_optionmenu_callback(x),
                                       variable=self.optionmenu_var2,
                                       width=150, state='disabled', corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=32, button_color="#FFFFFF", button_hover_color="#FFFFFF", dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF")
        self.combobox1.grid(row=0, column=4, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        self.optionmenu_var3 = ctk.StringVar(value="Column Y")
        self.combobox2 = ctk.CTkOptionMenu(master=frame1,
                                       values=[],
                                       command=lambda x: self.columnY_optionmenu_callback(x),
                                       variable=self.optionmenu_var3,
                                       width=150, state='disabled', corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=32, button_color="#FFFFFF", button_hover_color="#FFFFFF", dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF")
        self.combobox2.grid(row=0, column=5, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        label1 = ctk.CTkLabel(frame1, text="Bins number:", text_color="#FFFFFF", font=SMALLFONT)
        label1.grid(row=0, column=6, padx=0, pady=8, sticky="w")

        self.K_entry = ctk.CTkEntry(frame1, width=100, state='disabled')
        self.K_entry.grid(row=0, column=7, padx=8, pady=8)

        button3 = ctk.CTkButton(frame1, text="Plot", command=lambda: self.plot(self.K_entry.get()), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=32)
        button3.grid(row=0, column=8, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        frame2 = ctk.CTkFrame(self, fg_color="#101010")
        frame2.grid(row=2, column=0, columnspan=5, ipadx=8, ipady=8, sticky="nsew")

        self.figure = Figure(dpi=100)

        # create FigureCanvasTkAgg object
        self.figure_canvas = FigureCanvasTkAgg(self.figure, frame2)
        self.figure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # create the toolbar
        self.toolbar = NavigationToolbar2Tk(self.figure_canvas, frame2)
        self.toolbar.update()
        # create axes
        self.axes = self.figure.add_subplot()


    def plotType_optionmenu_callback(self, choice):
        """ if 'DATA' not in globals() or DATA.file_data is None:
            tk.messagebox.showerror("Information", "Please upload a data file first")
            return """
        
        self.visPlotType = choice
        print(self.visPlotType)
        
        if self.visPlotType == "Scatter plot":
            self.K_entry.configure(state="disabled")
            self.combobox1.configure(state="normal")
            self.combobox2.configure(state="normal")
        elif self.visPlotType == "Histogram":
            self.K_entry.configure(state="normal")
            self.combobox1.configure(state="normal")
            self.combobox2.configure(state="disabled")
        elif self.visPlotType == "Bar chart":
            self.K_entry.configure(state="disabled")
            self.combobox1.configure(state="normal")
            self.combobox2.configure(state="normal")
        elif self.visPlotType == "Line chart":
            self.K_entry.configure(state="disabled")
            self.combobox1.configure(state="normal")
            self.combobox2.configure(state="normal")
        elif self.visPlotType == "Box plot":
            self.K_entry.configure(state="disabled")
            self.combobox1.configure(state="normal")
            self.combobox2.configure(state="disabled")

    def columnX_optionmenu_callback(self, choice):
        """ if 'DATA' not in globals() or DATA.file_data is None:
            tk.messagebox.showerror("Information", "Please upload a data file first")
            return """
        
        self.visColumnX = choice
        print(self.visColumnX)
    
    def columnY_optionmenu_callback(self, choice):
        """ if 'DATA' not in globals() or DATA.file_data is None:
            tk.messagebox.showerror("Information", "Please upload a data file first")
            return """
        
        self.visColumnY = choice
        print(self.visColumnY)

    def plot(self, k=''):
        global DATA
        
        self.axes.clear()

        if self.visPlotType == "Scatter plot":
            if self.visColumnX == None or self.visColumnY == None or self.visColumnX == '' or self.visColumnY == '':
                tk.messagebox.showerror("Information", "Please select a column for X and Y")
                return
            self.axes.scatter(DATA.file_data[self.visColumnX], DATA.file_data[self.visColumnY])
            self.axes.set_xlabel(self.visColumnX)
            self.axes.set_ylabel(self.visColumnY)
            self.axes.set_title(f"{self.visColumnX} vs {self.visColumnY}")
        elif self.visPlotType == "Histogram":
            if self.visColumnX == None or self.visColumnX == '':
                tk.messagebox.showerror("Information", "Please select a column for X")
                return
            elif not k.isdigit():
                tk.messagebox.showerror("Information", "Please enter a valid value for k")
                return
            self.axes.hist(DATA.file_data[self.visColumnX], bins=int(k), linewidth=0.5, edgecolor="white")
            self.axes.set_xlabel(self.visColumnX)
            self.axes.set_title(f"{self.visColumnX} histogram")
        elif self.visPlotType == "Bar chart":
            if self.visColumnX == None or self.visColumnY == None or self.visColumnX == '' or self.visColumnY == '':
                tk.messagebox.showerror("Information", "Please select a column for X and Y")
                return
            self.axes.bar(DATA.file_data[self.visColumnX], DATA.file_data[self.visColumnY])
            self.axes.set_xlabel(self.visColumnX)
            self.axes.set_ylabel(self.visColumnY)
            self.axes.set_title(f"{self.visColumnX} vs {self.visColumnY}")
        elif self.visPlotType == "Line chart":
            if self.visColumnX == None or self.visColumnY == None or self.visColumnX == '' or self.visColumnY == '':
                tk.messagebox.showerror("Information", "Please select a column for X and Y")
                return
            self.axes.plot(DATA.file_data[self.visColumnX], DATA.file_data[self.visColumnY])
            self.axes.set_xlabel(self.visColumnX)
            self.axes.set_ylabel(self.visColumnY)
            self.axes.set_title(f"{self.visColumnX} vs {self.visColumnY}")
        elif self.visPlotType == "Box plot":
            if self.visColumnX == None or self.visColumnX == '':
                tk.messagebox.showerror("Information", "Please select a column for X")
                return
            self.axes.boxplot(DATA.file_data[self.visColumnX])
            self.axes.set_xlabel(self.visColumnX)
            self.axes.set_title(f"{self.visColumnX} box plot")

        self.figure_canvas.draw()
        self.toolbar.update()


class SaveDatasetPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)

        self.columnconfigure(0, weight=1)

        label = ctk.CTkLabel(self, text="Save dataset", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        frame = ctk.CTkFrame(self, fg_color="#101010")
        frame.grid(row=1, column=0, ipadx=0, ipady=0, columnspan=3, sticky="ew")

        frame.columnconfigure(1, weight=1)

        label1 = ctk.CTkLabel(frame, text="File name:", text_color="#FFFFFF", font=SMALLFONT)
        label1.grid(row=0, column=0, padx=(0, 10), pady=8, sticky = "w")

        self.K_entry = ctk.CTkEntry(frame, width=100, height=24, corner_radius=0)
        self.K_entry.grid(row=0, column=1, padx=(8, 0), pady=8, sticky="ew")   
        
        button1 = ctk.CTkButton(self, text="Choose directory", command=lambda: self.SelectSaveDirectory(), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48, width=56)
        button1.grid(row=2, column=0, padx=0, pady=(8, 4), sticky="ew")

        button3 = ctk.CTkButton(self, text="Save file", command=lambda: self.SaveFile(controller), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48, width=56)
        button3.grid(row=3, column=0, padx=0, pady=4, sticky="ew")

        button2 = ctk.CTkButton(self, text="Cancel", command=lambda: controller.show_frame(BlankPage), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48, width=56)
        button2.grid(row=4, column=0, padx=0, pady=4, sticky="ew")

    def SelectSaveDirectory(self):
        self.SaveDirectory = ctk.filedialog.askdirectory()
    
    def SaveFile(self, controller):
        global DATA
        
        if hasattr(self, 'SaveDirectory'):
            if self.SaveDirectory == None or self.SaveDirectory == '':
                tk.messagebox.showerror("Information", "Please select a directory")
                return
            elif self.K_entry.get() == None or self.K_entry.get() == '':
                tk.messagebox.showerror("Information", "Please enter a file name")
                return
            
            DATA.file_data.to_excel(self.SaveDirectory + "/" + self.K_entry.get() + ".xlsx", index=False)

            controller.show_frame(BlankPage)

        else:
            tk.messagebox.showerror("Information", "Please select a directory")
            return

class DataSplitPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((24, 24), Image.LANCZOS))
        continueImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").rotate(180).resize((24, 24), Image.LANCZOS))

        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)

        label = ctk.CTkLabel(self, text="Data splitting", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=0, pady=8, sticky = "w")

        frame1 = ctk.CTkFrame(self, fg_color="#101010")
        frame1.grid(row=1, column=0, ipadx=0, ipady=0, columnspan=3, sticky="ew")

        button1 = ctk.CTkButton(frame1, image=backImg, text="", command=lambda: controller.show_frame(DataProcessingPage), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48, width=56)
        button1.grid(row=0, column=0, padx=(0, 4), pady=8, sticky="w")

        button2 = ctk.CTkButton(frame1, text="Split data", command=lambda: self.split_train_test(K_entry.get(), K_entry1.get()), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48, width=56)
        button2.grid(row=0, column=1, padx=4, pady=8, sticky = "w")

        button5 = ctk.CTkButton(frame1, image=continueImg, text="", command=lambda: self.mlPage_switch(controller), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48, width=56)
        button5.grid(row=0, column=2, padx=4, pady=8, sticky="w")

        frame5 = ctk.CTkFrame(self, fg_color="#101010")
        frame5.grid(row=2, column=0, ipadx=0, ipady=0, columnspan=3, sticky="ew")

        label1 = ctk.CTkLabel(frame5, text="Test data ratio(default: 0.2):", text_color="#FFFFFF", font=SMALLFONT)
        label1.grid(row=0, column=0, padx=(0, 8), pady=8, sticky = "w")

        K_entry = ctk.CTkEntry(frame5, width=100, height=24)
        K_entry.grid(row=0, column=1, padx=8)

        frame6 = ctk.CTkFrame(self, fg_color="#101010")
        frame6.grid(row=3, column=0, ipadx=0, ipady=0, columnspan=3, sticky="ew")

        label2 = ctk.CTkLabel(frame6, text="Random state(default: 42):", text_color="#FFFFFF", font=SMALLFONT)
        label2.grid(row=0, column=0, padx=(0, 8), pady=8, sticky = "w")

        K_entry1 = ctk.CTkEntry(frame6, width=100, height=24)
        K_entry1.grid(row=0, column=1, padx=8)

        frame2 = ctk.CTkFrame(self, fg_color="#101010")
        #frame2.configure(fg_color="#101010")
        frame2.grid(row=4, column=0, columnspan=3,sticky="nsew")

        frame2.columnconfigure(0, weight=1)
        frame2.columnconfigure(1, weight=1)

        frame2.rowconfigure(0, weight=1)
        
        frame3 = ctk.CTkFrame(frame2, fg_color="#101010")
        frame3.grid(row=0, column=0, padx=(0, 12), sticky="nsew")
        
        frame4 = ctk.CTkFrame(frame2, fg_color="#101010")
        frame4.grid(row=0, column=1, padx=(12, 0), sticky="nsew")

        label1 = ctk.CTkLabel(frame3, text="Training data", pady=   24 , text_color="#FFFFFF", font=LARGEFONT)
        label1.pack(side="top", fill="both")

        self.TrainSheet = Sheet(frame3, data = None)
        self.TrainSheet.enable_bindings()
        self.TrainSheet.pack(side="top" , fill="both", expand=True)

        label2 = ctk.CTkLabel(frame4, text="Testing data", pady=24  , text_color="#FFFFFF", font=LARGEFONT)
        label2.pack(side="top", fill="both")

        self.TestSheet = Sheet(frame4, data = None)
        self.TestSheet.enable_bindings()
        self.TestSheet.pack(side="top" , fill="both", expand=True)

    """ def split_X_y(self):
        global DATA

        target_column = self.optionmenu_var2.get()
        target_column_type = DATA.file_data[target_column].dtype.name

        print(target_column_type)

        if DATA.mlModelType == 'Linear Regression':
            if target_column_type != 'int64' and target_column_type != 'float64' and target_column_type != 'int32' and target_column_type != 'float32':
                tk.messagebox.showerror("Information", "Please choose a valid target column for linear regression")
                return
        else: 
            if target_column_type == 'float64' or target_column_type == 'float32':
                tk.messagebox.showerror("Information", "Please choose a valid target column for classification")
                return

        if target_column is None or target_column == "":
            tk.messagebox.showerror("Information", "Choose a target class")
            return

        DATA.X = DATA.file_data.drop(target_column, axis=1)
        DATA.y = DATA.file_data[target_column] """

    def split_train_test(self, k='', random_state=''):
        global app
        global DATA
        
        if (k != '' and k != None) and (random_state != '' and random_state != None):
            try:
                k = float(k)
                random_state = int(random_state)

                if k <= 0 or k >= 1:
                    tk.messagebox.showerror("Value", "The value you chose for k is invalid")
                    return
            except ValueError:
                tk.messagebox.showerror("Information", "Please enter a valid value for k and random state")
                return
        
        elif (k != '' and k != None) and (random_state == '' or random_state == None):
            try:
                k = float(k)

                if k <= 0 or k >= 1:
                    tk.messagebox.showerror("Value", "The value you chose for k is invalid")
                    return
                
                random_state = 42
            except ValueError:
                tk.messagebox.showerror("Information", "Please enter a valid value for k")
                return
        
        elif (k == '' or k == None) and (random_state != '' and random_state != None):
            try:
                random_state = int(random_state)
                k = 0.2
            except ValueError:
                tk.messagebox.showerror("Information", "Please enter a valid value for random state")
                return
        
        else:
            k = 0.2
            random_state = 42
            
        DATA.X_train, DATA.X_test, DATA.y_train, DATA.y_test = train_test_split(DATA.X, DATA.y, test_size=k, random_state=random_state)
        
        self.TrainSheet.set_sheet_data(data = pd.concat([DATA.X_train, DATA.y_train], axis=1).values.tolist())
        self.TestSheet.set_sheet_data(data = pd.concat([DATA.X_test, DATA.y_test], axis=1).values.tolist())
    
    def mlPage_switch(self, controller):
        global app
        global DATA

        if DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None or DATA.X is None or DATA.y is None:
            tk.messagebox.showerror("Information", "Please split the data first")
            return

        app.frames[MLPage].label.configure(text=DATA.mlModelType)
        controller.show_frame(MLPage)

class MLPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        backImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((24, 24), Image.LANCZOS))

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        self.label = ctk.CTkLabel(self, text="Machine learning", text_color="#FFFFFF", font=LARGEFONT)
        self.label.grid(row=0, column=0, padx=0, pady=8, sticky = "w")

        self.frame1 = ctk.CTkFrame(self, fg_color="#101010")
        self.frame1.grid(row=1, column=0, ipadx=0, ipady=0, columnspan=3, sticky="ew")

        button1 = ctk.CTkButton(self.frame1, image=backImg, text="", command=lambda: controller.show_frame(DataSplitPage), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48, width=56)
        button1.grid(row=0, column=0, padx=(0, 4), pady=8, sticky = "w")

        self.optionmenu_var2 = ctk.StringVar(value="Model type")
        self.combobox2 = ctk.CTkOptionMenu(master=self.frame1,
                                       values=["Linear Regression", "Logistic Regression", "Decision Tree", "Naive Bayes", "Random Forest", "K-Nearest Neighbors (KNN)", "K-means", "Support Vector Machine (SVM)"],
                                       command=lambda x: self.optionmenu_callback(x),
                                       width=250,
                                       variable=self.optionmenu_var2, 
                                        corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=48, button_color="#FFFFFF", button_hover_color="#FFFFFF", dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF")
        self.combobox2.grid(row=0, column=1, padx=4, pady=8, sticky="w")

        button2 = ctk.CTkButton(self.frame1, text="Train model", command=lambda: self.train_mlModel(), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48)
        button2.grid(row=0, column=2, padx=4, pady=8, sticky = "w")
        
        self.button3 = ctk.CTkButton(self.frame1, text="Test model", command=lambda: self.test_mlModel(), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48, state="disabled")
        self.button3.grid(row=0, column=3, padx=4, pady=8, sticky = "w")

        self.button4 = ctk.CTkButton(self.frame1, text="Save model", command=lambda: self.openSaveModelWindow(), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48, state="disabled")
        self.button4.grid(row=0, column=4, padx=4, pady=8, sticky = "w")

        self.showMetricsPlotsBtn = ctk.CTkButton(self.frame1, text="Show classification metrics plots", command=lambda: self.showMetricsPlots(), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48, state="disabled")
        self.showMetricsPlotsBtn.grid(row=0, column=5, padx=4, pady=8, sticky = "w")
        
        self.frame2 = ctk.CTkFrame(self, fg_color="#101010", height=48)
        self.frame2.grid(row=2, column=0, pady=(1, 8), sticky="nsew")
        
        self.frame3 = ctk.CTkFrame(self, fg_color="#101010")
        self.frame3.grid(row=3, column=0, pady=(8, 0), sticky="nsew")
        
        self.rowconfigure(3, weight=1)
        self.frame3.columnconfigure(1, weight=1)
        self.frame3.columnconfigure(2, weight=1)
        self.frame3.rowconfigure(0, weight=1)

        self.frame4 = ctk.CTkFrame(self.frame3, fg_color="#101010")
        self.frame4.grid(row=0, column=0, sticky="nsew")

        self.frame5 = ctk.CTkFrame(self.frame3, fg_color="#101010")
        self.frame5.grid(row=0, column=1, padx=8,sticky="nsew")

        self.frame6 = ctk.CTkFrame(self.frame3, fg_color="#101010")
        self.frame6.grid(row=0, column=2, padx=0, sticky="nsew")

    def optionmenu_callback(self, choice: str):
        global DATA

        target_type = DATA.y.dtype.name

        if (target_type != 'int64' and target_type != 'float64' and target_type != 'int32' and target_type != 'float32' and choice in ["Linear Regression", "Decision tree"]) or ((target_type == 'float64' or target_type == 'float32') and choice not in ["Linear Regression", "Decision tree"]):
            tk.messagebox.showerror("Information", "Please choose a valid model for your chosen target column")
            return
        
        DATA.mlModelType = choice
        
        for widget in self.frame2.winfo_children():
            widget.destroy()

        if choice == 'Linear Regression':
            self.showMetricsPlotsBtn.configure(state="disabled")
            
        if choice == 'Decision Tree':
            CriterionLabel = ctk.CTkLabel(self.frame2, text="Criterion:", text_color="#FFFFFF", font=SMALLFONT)
            CriterionLabel.grid(row=0, column=0, padx=(0, 4), pady=4, sticky="w")

            self.optionmenu_var2 = ctk.StringVar(value="gini")
            self.dtCriterionBox = ctk.CTkOptionMenu(master=self.frame2,
                                       values=["gini", "entropy", "log_loss"],
                                       width=250,
                                       command=lambda x: print(x),
                                       variable=self.optionmenu_var2, 
                                       corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=48, button_color="#FFFFFF", button_hover_color="#FFFFFF", dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF")
            self.dtCriterionBox.grid(row=0, column=1, padx=4, pady=0, sticky="w")

            MaxDepthLabel = ctk.CTkLabel(self.frame2, text="Max depth:", text_color="#FFFFFF", font=SMALLFONT)
            MaxDepthLabel.grid(row=0, column=3, padx=(0, 4), sticky="w")

            self.dtMaxDepthEntry = ctk.CTkEntry(self.frame2, width=100, height=24)
            self.dtMaxDepthEntry.grid(row=0, column=4, padx=4, sticky="w")

            MinSamplesSplitLabel = ctk.CTkLabel(self.frame2, text="Min samples split:", text_color="#FFFFFF", font=SMALLFONT)
            MinSamplesSplitLabel.grid(row=0, column=5, padx=(0, 4), sticky="w")

            self.dtMinSamplesSplitEntry = ctk.CTkEntry(self.frame2, width=100, height=24)
            self.dtMinSamplesSplitEntry.grid(row=0, column=6, padx=4, sticky="w")
            
            RandomStateLabel = ctk.CTkLabel(self.frame2, text="Random state:", text_color="#FFFFFF", font=SMALLFONT)
            RandomStateLabel.grid(row=0, column=7, padx=(0, 4), sticky="w")

            self.dtRandomStateEntry = ctk.CTkEntry(self.frame2, width=100, height=24)
            self.dtRandomStateEntry.grid(row=0, column=8, padx=4, sticky="w")

            self.showMetricsPlotsBtn.configure(state="normal")

        elif choice == 'Logistic Regression':
            SolverLabel = ctk.CTkLabel(self.frame2, text="Solver:", text_color="#FFFFFF", font=SMALLFONT)
            SolverLabel.grid(row=0, column=0, padx=(0, 4), sticky="w")

            self.SolverVar = ctk.StringVar(value="lbfgs")
            self.lrSolverBox = ctk.CTkOptionMenu(master=self.frame2,
                                        values=["lbfgs", "liblinear", "sag", "saga", 'newton-cg', 'newton-cholesky'],
                                        width=250,
                                        variable=self.SolverVar, 
                                        corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=48, button_color="#FFFFFF", button_hover_color="#FFFFFF", dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF")
            self.lrSolverBox.grid(row=0, column=1, padx=4, pady=0, sticky="w")            

            PenaltyLabel = ctk.CTkLabel(self.frame2, text="Penalty:", text_color="#FFFFFF", font=SMALLFONT)
            PenaltyLabel.grid(row=0, column=2, padx=(0, 4), sticky="w")

            self.PenaltyVar = ctk.StringVar(value="l2")
            self.lrPenaltyBox = ctk.CTkOptionMenu(master=self.frame2,
                                       values=["l1", "l2", "elasticnet", "none"],
                                       width=250,
                                       variable=self.PenaltyVar, 
                                       corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=48, button_color="#FFFFFF", button_hover_color="#FFFFFF", dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF")
            self.lrPenaltyBox.grid(row=0, column=3, padx=4, sticky="w")

            CLabel = ctk.CTkLabel(self.frame2, text="C:", text_color="#FFFFFF", font=SMALLFONT)
            CLabel.grid(row=0, column=4, padx=(0, 4), sticky="w")

            self.lrCEntry = ctk.CTkEntry(self.frame2, width=100, height=24)
            self.lrCEntry.grid(row=0, column=5, padx=4, sticky="w")

            MaxIterLabel = ctk.CTkLabel(self.frame2, text="Max iter:", text_color="#FFFFFF", font=SMALLFONT)
            MaxIterLabel.grid(row=0, column=6, padx=(0, 4), sticky="w")

            self.lrMaxIterEntry = ctk.CTkEntry(self.frame2, width=100, height=24)
            self.lrMaxIterEntry.grid(row=0, column=7, padx=4, sticky="w")
            
            RandomStateLabel = ctk.CTkLabel(self.frame2, text="Random state:", text_color="#FFFFFF", font=SMALLFONT)
            RandomStateLabel.grid(row=0, column=8, padx=(0, 4), sticky="w")

            self.lrRandomStateEntry = ctk.CTkEntry(self.frame2, width=100, height=24)
            self.lrRandomStateEntry.grid(row=0, column=9, padx=4, sticky="w")

            self.showMetricsPlotsBtn.configure(state="normal")

        elif choice == 'Random Forest':
            CriterionLabel = ctk.CTkLabel(self.frame2, text="Criterion:", text_color="#FFFFFF", font=SMALLFONT)
            CriterionLabel.grid(row=0, column=0, padx=(0, 4), sticky="w")

            self.CriterionVar = ctk.StringVar(value="gini")
            self.rfCriterionBox = ctk.CTkOptionMenu(master=self.frame2,
                                       values=["gini", "entropy"],
                                       width=250,
                                       variable=self.CriterionVar, 
                                       corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=48, button_color="#FFFFFF", button_hover_color="#FFFFFF", dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF")
            self.rfCriterionBox.grid(row=0, column=1, padx=4, pady=0, sticky="w")

            MaxDepthLabel = ctk.CTkLabel(self.frame2, text="Max depth:", text_color="#FFFFFF", font=SMALLFONT)
            MaxDepthLabel.grid(row=0, column=3, padx=(0, 4), sticky="w")

            self.rfMaxDepthEntry = ctk.CTkEntry(self.frame2, width=100, height=24)
            self.rfMaxDepthEntry.grid(row=0, column=4, padx=4, sticky="w")

            MinSamplesSplitLabel = ctk.CTkLabel(self.frame2, text="Min samples split:", text_color="#FFFFFF", font=SMALLFONT)
            MinSamplesSplitLabel.grid(row=0, column=5, padx=(0, 4), sticky="w")

            self.rfMinSamplesSplitEntry = ctk.CTkEntry(self.frame2, width=100, height=24)
            self.rfMinSamplesSplitEntry.grid(row=0, column=6, padx=4, sticky="w")
            
            RandomStateLabel = ctk.CTkLabel(self.frame2, text="Random state:", text_color="#FFFFFF", font=SMALLFONT)
            RandomStateLabel.grid(row=0, column=7, padx=(0, 4), sticky="w")

            self.rfRandomStateEntry = ctk.CTkEntry(self.frame2, width=100, height=24)
            self.rfRandomStateEntry.grid(row=0, column=8, padx=4, sticky="w")

            self.showMetricsPlotsBtn.configure(state="normal")

        elif choice == 'K-Nearest Neighbors (KNN)':
            NNeighborsLabel = ctk.CTkLabel(self.frame2, text="N neighbors:", text_color="#FFFFFF", font=SMALLFONT)
            NNeighborsLabel.grid(row=0, column=0, padx=(0, 4), sticky="w")

            self.knnNNeighborsEntry = ctk.CTkEntry(self.frame2, width=100, height=24)
            self.knnNNeighborsEntry.grid(row=0, column=1, padx=4, sticky="w")

            AlgorithmLabel = ctk.CTkLabel(self.frame2, text="Algorithm:", text_color="#FFFFFF", font=SMALLFONT)
            AlgorithmLabel.grid(row=0, column=2, padx=(0, 4), sticky="w")

            self.AlgorithmVar = ctk.StringVar(value="auto")
            self.knnAlgorithmBox = ctk.CTkOptionMenu(master=self.frame2,
                                       values=["auto", "ball_tree", "kd_tree", "brute"],
                                       width=250,
                                       variable=self.AlgorithmVar, 
                                       corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=48, button_color="#FFFFFF", button_hover_color="#FFFFFF", dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF")
            self.knnAlgorithmBox.grid(row=0, column=3, padx=4, pady=0, sticky="w")

            LeafSizeLabel = ctk.CTkLabel(self.frame2, text="Leaf size:", text_color="#FFFFFF", font=SMALLFONT)
            LeafSizeLabel.grid(row=0, column=4, padx=(0, 4), sticky="w")

            self.knnLeafSizeEntry = ctk.CTkEntry(self.frame2, width=100, height=24)
            self.knnLeafSizeEntry.grid(row=0, column=5, padx=4, sticky="w")
            
            MetricLabel = ctk.CTkLabel(self.frame2, text="Metric:", text_color="#FFFFFF", font=SMALLFONT)
            MetricLabel.grid(row=0, column=6, padx=(0, 4), sticky="w")

            self.optionmenu_var2 = ctk.StringVar(value="minkowski")
            self.knnMetricBox = ctk.CTkOptionMenu(master=self.frame2,
                                        values=["euclidean", "manhattan", "chebyshev", "minkowski", "wminkowski", "seuclidean", "mahalanobis"],
                                        width=250,
                                        variable=self.optionmenu_var2, 
                                        corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=48, button_color="#FFFFFF", button_hover_color="#FFFFFF", dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF")
            self.knnMetricBox.grid(row=0, column=7, padx=4, pady=0, sticky="w")

            self.showMetricsPlotsBtn.configure(state="normal")

        elif choice == 'K-means':
            NClustersLabel = ctk.CTkLabel(self.frame2, text="N clusters:", text_color="#FFFFFF", font=SMALLFONT)
            NClustersLabel.grid(row=0, column=0, padx=(0, 4), sticky="w")

            self.kmNClustersEntry = ctk.CTkEntry(self.frame2, width=100, height=24)
            self.kmNClustersEntry.grid(row=0, column=1, padx=4, sticky="w")

            MaxIterLabel = ctk.CTkLabel(self.frame2, text="Max iter:", text_color="#FFFFFF", font=SMALLFONT)
            MaxIterLabel.grid(row=0, column=3, padx=(0, 4), sticky="w")

            self.kmMaxIterEntry = ctk.CTkEntry(self.frame2, width=100, height=24)
            self.kmMaxIterEntry.grid(row=0, column=4, padx=4, sticky="w")

            AlgorithmLabel = ctk.CTkLabel(self.frame2, text="Algorithm:", text_color="#FFFFFF", font=SMALLFONT)
            AlgorithmLabel.grid(row=0, column=5, padx=(0, 4), sticky="w")

            self.AlgorithmVar = ctk.StringVar(value="auto")
            self.kmAlgorithmBox = ctk.CTkOptionMenu(master=self.frame2,
                                       values=["auto", "full", "elkan"],
                                       width=250,
                                       variable=self.AlgorithmVar, 
                                       corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=48, button_color="#FFFFFF", button_hover_color="#FFFFFF", dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF")
            self.kmAlgorithmBox.grid(row=0, column=6, padx=4, pady=0, sticky="w")
            
            RandomStateLabel = ctk.CTkLabel(self.frame2, text="Random state:", text_color="#FFFFFF", font=SMALLFONT)
            RandomStateLabel.grid(row=0, column=7, padx=(0, 4), sticky="w")

            self.kmRandomStateEntry = ctk.CTkEntry(self.frame2, width=100, height=24)
            self.kmRandomStateEntry.grid(row=0, column=8, padx=4, sticky="w")

            self.showMetricsPlotsBtn.configure(state="normal")

        elif choice == 'Support Vector Machine (SVM)':
            CLabel = ctk.CTkLabel(self.frame2, text="C:", text_color="#FFFFFF", font=SMALLFONT)
            CLabel.grid(row=0, column=0, padx=(0, 4), sticky="w")

            self.svmCEntry = ctk.CTkEntry(self.frame2, width=100, height=24)
            self.svmCEntry.grid(row=0, column=1, padx=4, sticky="w")

            KernelLabel = ctk.CTkLabel(self.frame2, text="Kernel:", text_color="#FFFFFF", font=SMALLFONT)
            KernelLabel.grid(row=0, column=3, padx=(0, 4), sticky="w")

            self.KernelVar = ctk.StringVar(value="rbf")
            self.svmKernelBox = ctk.CTkOptionMenu(master=self.frame2,
                                       values=["linear", "poly", "rbf", "sigmoid", "precomputed"],
                                       width=250,
                                       variable=self.KernelVar, 
                                       corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=48, button_color="#FFFFFF", button_hover_color="#FFFFFF", dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF")
            self.svmKernelBox.grid(row=0, column=4, padx=4, pady=0, sticky="w")

            GammaLabel = ctk.CTkLabel(self.frame2, text="Gamma:", text_color="#FFFFFF", font=SMALLFONT)
            GammaLabel.grid(row=0, column=5, padx=(0, 4), sticky="w")

            self.svmGammaEntry = ctk.CTkEntry(self.frame2, width=100, height=24)
            self.svmGammaEntry.grid(row=0, column=6, padx=4, sticky="w")
            
            RandomStateLabel = ctk.CTkLabel(self.frame2, text="Random state:", text_color="#FFFFFF", font=SMALLFONT)
            RandomStateLabel.grid(row=0, column=7, padx=(0, 4), sticky="w")

            self.svmRandomStateEntry = ctk.CTkEntry(self.frame2, width=100, height=24)
            self.svmRandomStateEntry.grid(row=0, column=8, padx=4, sticky="w")

            self.showMetricsPlotsBtn.configure(state="normal")

    def train_mlModel(self):
        global DATA

        if self.combobox2.get() == 'Model type':
            tk.messagebox.showerror("Information", "Please choose a model type")
            return
        
        if DATA.mlModelType == 'Linear Regression':
            DATA.mlModel = LinearRegression()

        elif DATA.mlModelType == 'Decision Tree':
            dtCriterion = self.dtCriterionBox.get()
            dtMaxDepth = self.dtMaxDepthEntry.get()
            dtMinSamplesSplit = self.dtMinSamplesSplitEntry.get()
            dtRandomState = self.dtRandomStateEntry.get()

            if dtCriterion == '' or dtCriterion == None:
                dtCriterion = 'gini'
            if dtMaxDepth == '':
                dtMaxDepth = None
            else:
                try:
                    dtMaxDepth = int(dtMaxDepth)
                except:
                    dtMaxDepth = None 
            if dtMinSamplesSplit == '':
                dtMinSamplesSplit = 2
            else:
                try:
                    dtMinSamplesSplit = float(dtMinSamplesSplit)
                except:
                    dtMinSamplesSplit = 2
            if dtRandomState == '':
                dtRandomState = 42
            else:
                try:
                    dtRandomState = int(dtRandomState)
                except:
                    dtRandomState = 42

            DATA.mlModel = DecisionTreeClassifier(criterion=dtCriterion, max_depth=dtMaxDepth, min_samples_split=dtMinSamplesSplit, random_state=dtRandomState)

        elif DATA.mlModelType == 'Logistic Regression':
            lrSolver = self.lrSolverBox.get()
            lrPenalty = self.lrPenaltyBox.get()
            lrC = self.lrCEntry.get()
            lrMaxIter = self.lrMaxIterEntry.get()
            lrRandomState = self.lrRandomStateEntry.get()
            
            if lrSolver == '' or lrSolver == None:
                lrSolver = 'lbfgs'
            if lrPenalty == '' or lrPenalty == None:
                lrPenalty = 'l2'
            if lrC == '':
                lrC = 1.0
            else:
                try:
                    lrC = float(lrC)
                except:
                    lrC = 1.0
            if lrMaxIter == '':
                lrMaxIter = 100
            else:
                try:
                    lrMaxIter = int(lrMaxIter)
                except:
                    lrMaxIter = 100
            if lrRandomState == '':
                lrRandomState = 42
            else:
                try:
                    lrRandomState = int(lrRandomState)
                except:
                    lrRandomState = 42
            
            if (lrSolver in ['lbfgs', 'sag', 'newton-cg', 'newton-cholesky'] and lrPenalty not in ['l2', None]) or (lrSolver == 'liblinear' and lrPenalty not in ['l1', 'l2']):
                tk.messagebox.showerror("Information", "Please choose a valid penalty for the chosen solver")
                return
            

            DATA.mlModel = LogisticRegression(penalty=lrPenalty, C=lrC, max_iter=lrMaxIter, random_state=lrRandomState)

        elif DATA.mlModelType == 'Random Forest':   
            rfCriterion = self.rfCriterionBox.get()
            rfMaxDepth = self.rfMaxDepthEntry.get()
            rfMinSamplesSplit = self.rfMinSamplesSplitEntry.get()
            rfRandomState = self.rfRandomStateEntry.get()

            if rfCriterion == '' or rfCriterion == None:
                rfCriterion = 'gini'
            if rfMaxDepth == '':
                rfMaxDepth = None
            else:
                try:
                    rfMaxDepth = int(rfMaxDepth)
                except:
                    rfMaxDepth = None 
            if rfMinSamplesSplit == '':
                rfMinSamplesSplit = 2
            else:
                try:
                    rfMinSamplesSplit = float(rfMinSamplesSplit)
                except:
                    rfMinSamplesSplit = 2
            if rfRandomState == '':
                rfRandomState = 42
            else:
                try:
                    rfRandomState = int(rfRandomState)
                except:
                    rfRandomState = 42

            DATA.mlModel = RandomForestClassifier(criterion=rfCriterion, max_depth=rfMaxDepth, min_samples_split=rfMinSamplesSplit, random_state=rfRandomState)

        elif DATA.mlModelType == 'K-Nearest Neighbors (KNN)':
            knnNNeighbors = self.knnNNeighborsEntry.get()
            knnAlgorithm = self.knnAlgorithmBox.get()
            knnLeafSize = self.knnLeafSizeEntry.get()
            knnMetric = self.knnMetricBox.get()

            if knnNNeighbors == '':
                knnNNeighbors = 5
            else:
                try:
                    knnNNeighbors = int(knnNNeighbors)
                except:
                    knnNNeighbors = 5
            if knnAlgorithm == '' or knnAlgorithm == None:
                knnAlgorithm = 'auto'
            if knnLeafSize == '':
                knnLeafSize = 30
            else:
                try:
                    knnLeafSize = int(knnLeafSize)
                except:
                    knnLeafSize = 30
            if knnMetric == '' or knnMetric == None:
                knnMetric = 'minkowski'

            DATA.mlModel = KNeighborsClassifier(n_neighbors=knnNNeighbors, algorithm=knnAlgorithm, leaf_size=knnLeafSize, metric=knnMetric)

        elif DATA.mlModelType == 'K-means':
            kmNClusters = self.kmNClustersEntry.get()
            kmMaxIter = self.kmMaxIterEntry.get()
            kmAlgorithm = self.kmAlgorithmBox.get()
            kmRandomState = self.kmRandomStateEntry.get()

            if kmNClusters == '':
                kmNClusters = 8
            else:
                try:
                    kmNClusters = int(kmNClusters)
                except:
                    kmNClusters = 8
            if kmMaxIter == '':
                kmMaxIter = 300
            else:
                try:
                    kmMaxIter = int(kmMaxIter)
                except:
                    kmMaxIter = 300
            if kmAlgorithm == '' or kmAlgorithm == None:
                kmAlgorithm = 'auto'
            if kmRandomState == '':
                kmRandomState = 42
            else:
                try:
                    kmRandomState = int(kmRandomState)
                except:
                    kmRandomState = 42

            DATA.mlModel = KMeans(n_clusters=kmNClusters, max_iter=kmMaxIter, algorithm=kmAlgorithm, random_state=kmRandomState)

        elif DATA.mlModelType == 'Support Vector Machine (SVM)':
            svmC = self.svmCEntry.get()
            svmKernel = self.svmKernelBox.get()
            svmGamma = self.svmGammaEntry.get()
            svmRandomState = self.svmRandomStateEntry.get()

            if svmC == '':
                svmC = 1.0
            else:
                try:
                    svmC = float(svmC)
                except:
                    svmC = 1.0
            if svmKernel == '' or svmKernel == None:
                svmKernel = 'rbf'
            if svmGamma == '':
                svmGamma = 'scale'
            else:
                try:
                    svmGamma = float(svmGamma)
                except:
                    svmGamma = 'scale'
            if svmRandomState == '':
                svmRandomState = 42
            else:
                try:
                    svmRandomState = int(svmRandomState)
                except:
                    svmRandomState = 42

            DATA.mlModel = svm.SVC(C=svmC, kernel=svmKernel, gamma=svmGamma, random_state=svmRandomState)

        

        DATA.mlModel.fit(DATA.X_train, DATA.y_train)

        self.button3.configure(state="normal")
        self.button4.configure(state="normal")
        """ if DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None:
            print('DATA.X', DATA.X)
            print('DATA.y', DATA.y)
            DATA.mlModel.fit(DATA.X, DATA.y)
            print('Model fitted')
        else:
            DATA.mlModel.fit(DATA.X_train, DATA.y_train)
            print('Model fitted') """

    def test_mlModel(self):
        global DATA

        """ if DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None:
            print('DATA.X', DATA.X)
            print('DATA.y', DATA.y)
            prediction = DATA.mlModel.predict(DATA.X)
        else:
            prediction = DATA.mlModel.predict(DATA.X_test) """
        self.prediction = DATA.mlModel.predict(DATA.X_test)
        print(DATA.mlModel)
        print(self.prediction)

        if DATA.mlModelType == 'Linear Regression':
            self.label1 = ctk.CTkLabel(self.frame4, text=f"Max error: {round(metrics.max_error(DATA.y_test, self.prediction), 4)}", text_color="#FFFFFF", font=LARGEFONT)
            self.label1.grid(row=2, column=0, padx=0, pady=8, sticky = "w")

            self.label2 = ctk.CTkLabel(self.frame4, text=f"Mean absolute error: {round(metrics.mean_absolute_error(DATA.y_test, self.prediction), 4)}", text_color="#FFFFFF", font=LARGEFONT)
            self.label2.grid(row=3, column=0, padx=0, pady=8, sticky = "w")

            self.label3 = ctk.CTkLabel(self.frame4, text=f"Mean squared error: {round(metrics.mean_squared_error(DATA.y_test, self.prediction), 4)}", text_color="#FFFFFF", font=LARGEFONT)
            self.label3.grid(row=4, column=0, padx=0, pady=8, sticky = "w")

            self.label4 = ctk.CTkLabel(self.frame4, text=f"R2 score: {round(metrics.r2_score(DATA.y_test, self.prediction), 4)}", text_color="#FFFFFF", font=LARGEFONT)
            self.label4.grid(row=5, column=0, padx=0, pady=8, sticky = "w")

        else:
            self.cm = metrics.confusion_matrix(DATA.y_test, self.prediction)
            BER = 1 - (1/2 * ((self.cm[0][0] / (self.cm[0][0] + self.cm[1][0])) + (self.cm[1][1] / (self.cm[1][1] + self.cm[0][1]))))
    
            self.label1 = ctk.CTkLabel(self.frame4, text=f"Balanced Error Rate: {round(BER, 4)}", text_color="#FFFFFF", font=LARGEFONT)
            self.label1.grid(row=3, column=0, padx=0, pady=8, sticky = "w")

            self.label2 = ctk.CTkLabel(self.frame4, text=f"Accuracy: {round(metrics.accuracy_score(DATA.y_test, self.prediction), 4)}", text_color="#FFFFFF", font=LARGEFONT)
            self.label2.grid(row=4, column=0, padx=0, pady=8, sticky = "w")

            self.label3 = ctk.CTkLabel(self.frame4, text=f"Precision: {round(metrics.precision_score(DATA.y_test, self.prediction), 4)}", text_color="#FFFFFF", font=LARGEFONT)
            self.label3.grid(row=5, column=0, padx=0, pady=8, sticky = "w")

            self.label4 = ctk.CTkLabel(self.frame4, text=f"Recall: {round(metrics.recall_score(DATA.y_test, self.prediction), 4)}", text_color="#FFFFFF", font=LARGEFONT)
            self.label4.grid(row=6, column=0, padx=0, pady=8, sticky = "w")

            self.label5 = ctk.CTkLabel(self.frame4, text=f"F1 score: {round(metrics.f1_score(DATA.y_test, self.prediction), 4)}", text_color="#FFFFFF", font=LARGEFONT)
            self.label5.grid(row=7, column=0, padx=0, pady=8, sticky = "w")

            self.label6 = ctk.CTkLabel(self.frame4, text=f"AUC score: {round(metrics.roc_auc_score(DATA.y_test, self.prediction), 4)}", text_color="#FFFFFF", font=LARGEFONT)
            self.label6.grid(row=8, column=0, padx=0, pady=8, sticky = "w")

    # BUG: i get an error after ploting after testing the model, ploting metrics plots and closing the window
    #       This error is indicating that your program is trying to execute a command called 2577533870784update, but this command does not exist. This command looks like it might be the result of 
    #       some kind of string concatenation error, where a memory address (the number) is being concatenated with a command name (update). This could be happening if you're trying to update a 
    #       widget after it has been destroyed.
    """ def showMetricsPlots(self):
        global DATA
        global app
        
        if DATA.mlModelType != 'Linear Regression' :
            if app.winfo_exists():
                disp = metrics.ConfusionMatrixDisplay.from_predictions(y_true=DATA.y_test, y_pred=self.prediction, display_labels=["False", "True"], cmap=plt.cm.Blues)
                fpr, tpr, thresh = metrics.roc_curve(DATA.y_test, self.prediction, pos_label=1)
                roc_display = metrics.RocCurveDisplay(fpr=fpr, tpr=tpr)

                self.figure1 = Figure()

                # create FigureCanvasTkAgg object
                self.figure_canvas1 = FigureCanvasTkAgg(self.figure1, self.frame5)

                # create axes
                self.axe1 = self.figure1.add_subplot()

                disp.plot(ax=self.axe1)
                self.axe1.legend([""], fontsize="x-large")
                self.axe1.set_xlabel("")
                self.axe1.set_title("Confusion matrix")

                self.figure2 = Figure()

                # create FigureCanvasTkAgg object
                self.figure_canvas2 = FigureCanvasTkAgg(self.figure2, self.frame6)

                # create axes
                self.axe2 = self.figure2.add_subplot()

                roc_display.plot(ax=self.axe2)
                self.axe1.legend([""], fontsize="x-large")
                self.axe1.set_xlabel("")
                self.axe1.set_title("ROC curve")

                self.figure_canvas1.draw()
                self.figure_canvas2.draw()
                self.figure_canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                self.figure_canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            if app.window_closed:
                return """

    def openSaveModelWindow(self):
        try:
            DATA.mlModel.predict(DATA.X_test)
        except NotFittedError:
            tk.messagebox.showerror("Information", "Please train your model")
            return
        
        SaveModelWindow = SaveModelTopLevel()
        SaveModelWindow.grab_set()

class SaveModelTopLevel(ctk.CTkToplevel):
    def __init__(self):
        ctk.CTkToplevel.__init__(self)
        
        self.resizable(False, False)
        self.geometry("300x270")
        self.iconbitmap('./assets/icons/machine-learning.ico')
        self.configure(bg_color="#101010", fg_color="#101010", width=200)
        self.title("Save model")

        self.columnconfigure(0, weight=1)

        label = ctk.CTkLabel(self, text="Save model", text_color="#FFFFFF", font=LARGEFONT)
        label.grid(row=0, column=0, padx=8, pady=8, sticky="w")

        frame = ctk.CTkFrame(self, fg_color="#191919")
        frame.grid(row=1, column=0, ipadx=0, ipady=0, columnspan=3, sticky="ew")

        frame.columnconfigure(1, weight=1)

        label1 = ctk.CTkLabel(frame, text="File name:", text_color="#FFFFFF", font=SMALLFONT)
        label1.grid(row=0, column=0, padx=8, pady=8, sticky = "w")

        self.FileName_entry = ctk.CTkEntry(frame, width=100, height=24)
        self.FileName_entry.grid(row=0, column=1, padx=8, pady=8, sticky="ew")

        button1 = ctk.CTkButton(self, text="Choose directory", command=lambda: self.SelectSaveDirectory(), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48, width=56)
        button1.grid(row=2, column=0, padx=8, pady=(8, 4), sticky="ew")

        button3 = ctk.CTkButton(self, text="Save file", command=lambda: self.SaveFile(), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48, width=56)
        button3.grid(row=3, column=0, padx=8, pady=4, sticky="ew")

    def SelectSaveDirectory(self):
        self.SaveDirectory = ctk.filedialog.askdirectory()
    
    def SaveFile(self):
        global DATA
        if hasattr(self, 'SaveDirectory'):
            if self.SaveDirectory == None or self.SaveDirectory == '':
                tk.messagebox.showerror("Information", "Please select a directory")
                return
            elif self.FileName_entry.get() == None or self.FileName_entry.get() == '':
                tk.messagebox.showerror("Information", "Please enter a file name")
                return
            
            joblib.dump(DATA.file_data, self.SaveDirectory + "/" + self.FileName_entry.get() + ".sav")

            self.exitTopLevel()
        else:
            tk.messagebox.showerror("Information", "Please select a directory")
            return
        
# DRIVER CODE
app = App()
app.mainloop()
