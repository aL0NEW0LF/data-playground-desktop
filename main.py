from hmac import new
from sklearn.feature_selection import VarianceThreshold
from assets.fonts.fonts import LARGEFONT, MEDIUMFONT, SMALLFONT
import tkinter as tk
from tkinter import ttk
import os
import customtkinter as ctk
from PIL import ImageTk, Image
from joblib import dump, load
from matplotlib import axis, pyplot as plt
from pandas import concat
from sklearn.calibration import LabelEncoder
from sklearn.exceptions import NotFittedError
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import BernoulliNB, GaussianNB, MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn import metrics, svm
from sklearn.cluster import KMeans
from logic.file_handling import file_handling as fh
from tksheet import Sheet
from logic.data_preprocessing import feature_selection_kBestFeatures, feature_selection_varianceThreshold, handle_missing_values, drop_duplicate_rows, drop_contant_columns, get_non_numeric_columns, get_dataframe_columns, get_non_constant_columns, get_constant_columns, remove_outliers
from enums import enums
import matplotlib
from numpy import float64, float32

matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)

MLModels = {'Linear Regression': LinearRegression(), 'Decision Tree': DecisionTreeClassifier(), 'Naive Bayes': GaussianNB(), 'Support Vector Machine (SVM)': svm.SVC(), 'K-means': KMeans(), 'K-Nearest Neighbors (KNN)': KNeighborsClassifier(), 'Random Forest': RandomForestClassifier(), 'Logistic Regression': LogisticRegression()}
DATA = fh()

# WRAPPER FUNCTIONS
def UploadAction(type: str = 'file'):
    file_path = ctk.filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("JSON files", "*.json"), ("Text files", "*.txt")] if type == 'file' else [(".SAV files", "*.sav")])
    _, file_extension = os.path.splitext(file_path)

    return file_path, file_extension

def read_data():
    global DATA
    DATA.file_data_read()
    print(DATA)

def Exit():
    plt.close()
    app.quit()

# MAIN APP
class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        ctk.CTk.__init__(self, *args, **kwargs)

        self.geometry("1380x720")
        self.iconbitmap('./assets/icons/machine-learning.ico')
        self.title("Data playground")
        self.minsize(1380, 720)
        self.configure(fg_color="#101010")

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
    
# first window frame startpage
class StartPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)

        frame = ctk.CTkFrame(self)
        frame.configure(fg_color="#101010")
        frame.place(relx=0.5, rely=0.5, anchor="c")

        label = ctk.CTkLabel(frame,
                             text="Let's get started! Please upload your dataset\n\n(Files supported: .xlsx / .csv / .json / .txt)",
                             text_color="#FFFFFF", font=LARGEFONT,
                             fg_color="#101010")
        label.grid(row=0, column=0, padx=0, pady=(100, 8), sticky="n")

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
        UploadButton.grid(row=1, column=0, padx=20, pady=36, sticky="nsew")

    def button_click_controller(self, btn: ctk.CTkButton, controller):
        global DATA 

        DATA.mlModelType = btn.cget('text')
        DATA.mlModel = MLModels[DATA.mlModelType]
        print(DATA.mlModelType)
        controller.show_frame(DataProcessingPage)

    def upload_data(self, controller):
        file_path, file_extension = UploadAction()

        if file_path == "":
            tk.messagebox.showerror("Information", "Please upload a data file first")
            return
        
        if file_extension not in ['.xlsx', '.csv', '.json', '.txt']:
            tk.messagebox.showerror("Information", "Please upload a valid data file")
            return

        global DATA

        DATA.file_path = file_path
        DATA.file_extension = file_extension

        DATA.file_data_read()

        app.frames[DataProcessingPage].load_data()

        app.frames[DataProcessingPage].TargetColumnCombobox.configure(values=get_dataframe_columns(DATA.file_data))

        app.frames[DataProcessingPage].TargetColumnCombobox.configure(state='normal')

        controller.show_frame(DataProcessingPage)

class DataProcessingPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)

        continueImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").rotate(180).resize((24, 24), Image.LANCZOS))

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        Title = ctk.CTkLabel(self, text="Data processing", text_color="#FFFFFF", font=LARGEFONT, bg_color="#101010",
                             fg_color="#101010")
        Title.grid(row=0, column=0, columnspan=5, padx=0, pady=8, sticky="nw")

        ButtonsFrame = ctk.CTkFrame(self, fg_color="#101010")
        ButtonsFrame.grid(row=1, column=0, sticky="ew")

        self.UploadButton = ctk.CTkButton(ButtonsFrame, text="Upload your data", command=lambda: self.upload_data(),
                                          corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF",
                                          font=SMALLFONT, hover_color="#F0F0F0", height=48)
        self.UploadButton.grid(row=0, column=0, padx=(0, 4), pady=8, sticky="w")

        self.TargetColumnOptionmenuVar = ctk.StringVar(value="Target column")
        self.TargetColumnCombobox = ctk.CTkOptionMenu(master=ButtonsFrame,
                                                      values=[],
                                                      variable=self.TargetColumnOptionmenuVar,
                                                      state='disabled',
                                                      command=lambda x: self.split_X_y(x), corner_radius=0,
                                                      text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF",
                                                      font=SMALLFONT, height=48, width=146, button_color="#FFFFFF",
                                                      button_hover_color="#FFFFFF", dropdown_font=SMALLFONT,
                                                      dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF",
                                                      dropdown_text_color="#101010")
        self.TargetColumnCombobox.grid(row=0, column=1, padx=4, pady=8, sticky="w")

        self.VisualizeButton = ctk.CTkButton(ButtonsFrame, text="Visualize",
                                             command=lambda: self.VisPageSwitch(controller=controller),
                                             state='disabled', corner_radius=0, text_color="#101010",
                                             bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT,
                                             hover_color="#F0F0F0", height=48)
        self.VisualizeButton.grid(row=0, column=2, padx=4, pady=8, sticky="w")

        self.SaveDatasetButton = ctk.CTkButton(ButtonsFrame, text="Save dataset",
                                               command=lambda: self.show_frame(SaveDatasetPage), state='disabled',
                                               corner_radius=0, text_color="#101010", bg_color="#FFFFFF",
                                               fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48)
        self.SaveDatasetButton.grid(row=0, column=3, padx=4, pady=8, sticky="w")

        self.ContinueButton = ctk.CTkButton(ButtonsFrame, image=continueImg, text="",
                                            command=lambda: self.SplitPageSwitch(controller), state='disabled',
                                            corner_radius=0, text_color="#101010", bg_color="#FFFFFF",
                                            fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=48,
                                            width=56)
        self.ContinueButton.grid(row=0, column=4, padx=4, pady=8, sticky="w")

        DataProcessingMainFrame = ctk.CTkFrame(self, fg_color="#101010")
        DataProcessingMainFrame.grid(row=2, column=0, columnspan=5, ipadx=8, ipady=8, sticky="nsew")

        DataProcessingMainFrame.rowconfigure(0, weight=1)
        DataProcessingMainFrame.columnconfigure(1, weight=1)

        ProcessingFrame = ctk.CTkFrame(DataProcessingMainFrame, fg_color="#101010", width=358)
        ProcessingFrame.grid(row=0, column=0, padx=(0, 8), pady=0, ipadx=0, ipady=0, sticky="nw")
        ProcessingFrame.rowconfigure(1, weight=1)

        ProcessingButtonsFrame = ctk.CTkFrame(ProcessingFrame, fg_color="#101010", width=358)
        ProcessingButtonsFrame.grid(row=0, column=0, padx=0, pady=0, ipadx=0, ipady=0, sticky="nw")

        separator = ttk.Separator(ProcessingFrame, orient='horizontal')
        separator.grid(row=1, column=0, padx=0, pady=0, ipadx=0, ipady=0, sticky="ew")

        self.ProcessingHandlingFrame = ctk.CTkFrame(ProcessingFrame, fg_color="#101010", width=358)
        self.ProcessingHandlingFrame.grid(row=2, column=0, padx=0, pady=0, ipadx=0, ipady=0, sticky="nw")

        self.FeatureSelectionOptionmenuVar = ctk.StringVar(value="Features selection")
        self.FeatureSelectionCombobox = ctk.CTkOptionMenu(master=ProcessingButtonsFrame,
                                                          values=["Variance threshold", "K-best features"],
                                                          command=lambda x: self.optionmenu_callback(x),
                                                          variable=self.FeatureSelectionOptionmenuVar,
                                                          state='disabled', corner_radius=0, text_color="#101010",
                                                          bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT,
                                                          height=48, width=175, button_color="#FFFFFF",
                                                          button_hover_color="#FFFFFF", dropdown_font=SMALLFONT,
                                                          dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF",
                                                          dropdown_text_color="#101010")
        self.FeatureSelectionCombobox.grid(row=0, column=0, padx=(0, 4), pady=(0, 8), sticky="w")

        self.ProcessingOptionmenuVar = ctk.StringVar(value="Preprocessing")
        self.ProcessingCombobox = ctk.CTkOptionMenu(master=ProcessingButtonsFrame,
                                                    values=["Missing values", "Duplicate rows", "Constant features",
                                                            "Outliers", "Remove columns", "Label encoding"],
                                                    command=lambda x: self.optionmenu_callback(x),
                                                    variable=self.ProcessingOptionmenuVar,
                                                    state='disabled', corner_radius=0, text_color="#101010",
                                                    bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=48,
                                                    width=175, button_color="#FFFFFF", button_hover_color="#FFFFFF",
                                                    dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0",
                                                    dropdown_fg_color="#FFFFFF", dropdown_text_color="#101010")
        self.ProcessingCombobox.grid(row=0, column=1, padx=(4, 0), pady=(0, 8), sticky="w")

        SheetFrame = ctk.CTkFrame(DataProcessingMainFrame, fg_color="#101010")
        SheetFrame.grid(row=0, column=1, ipadx=0, ipady=0, sticky="nsew")

        self.sheet = Sheet(SheetFrame, data=None)
        self.sheet.enable_bindings()
        self.sheet.pack(side="top" , fill="both", expand=True)

        self.frames = {}

        for F in (VarianceThresholdPage, KbestfeatPage, MissingValuesPage, DuplicateRowsPage, ConstantFeaturesPage, OutliersPage, RemoveColumnsPage, LabelEncodingPage, SaveDatasetPage, BlankPage):
            frame = F(self.ProcessingHandlingFrame, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(BlankPage)
        
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.configure(fg_color="#101010", width=358)
        frame.tkraise()

    def upload_data(self):
        file_path, file_extension = UploadAction()
        
        if file_path == "":
            return
        
        if file_extension not in ['.xlsx', '.csv', '.json', '.txt']:
            tk.messagebox.showerror("Information", "Please upload a valid data file")
            return

        global DATA

        DATA.file_path = file_path
        DATA.file_extension = file_extension

        DATA.file_data_read()

        self.load_data()

        self.TargetColumnCombobox.configure(values=get_dataframe_columns(DATA.file_data))

        self.TargetColumnCombobox.configure(state='normal')
        self.FeatureSelectionCombobox.configure(state='disabled')
        self.ProcessingCombobox.configure(state='disabled')
        self.VisualizeButton.configure(state='disabled')
        self.SaveDatasetButton.configure(state='disabled')
        self.ContinueButton.configure(state='disabled')

    def load_data(self):
        global app
        global DATA
        self.sheet.set_sheet_data(data=DATA.file_data.values.tolist())

    def optionmenu_callback(self, choice):
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
            self.frames[LabelEncodingPage].ColumnsCombobox.configure(values=get_non_numeric_columns(DATA.file_data))
            self.show_frame(LabelEncodingPage)

    def VisPageSwitch(self, controller):
        if 'DATA' not in globals() or DATA.file_data is None:
            tk.messagebox.showerror("Information", "Please upload a data file first")
            return
        
        global app
        app.frames[VisualizationPage].ColumnXCombobox.configure(values=get_dataframe_columns(DATA.file_data))
        app.frames[VisualizationPage].ColumnYCombobox.configure(values=get_dataframe_columns(DATA.file_data))
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

        if choice is None or choice == "":
            tk.messagebox.showerror("Information", "Choose a target class")
            return

        DATA.target_column = choice

        print(DATA.target_column)

        DATA.X = DATA.file_data.drop(DATA.target_column, axis=1)
        DATA.y = DATA.file_data[DATA.target_column]

        DATA.file_data = concat([DATA.X, DATA.y], axis=1)

        self.load_data()

        self.FeatureSelectionCombobox.configure(state='normal')
        self.ProcessingCombobox.configure(state='normal')
        self.VisualizeButton.configure(state='normal')
        self.ContinueButton.configure(state='normal')
        self.SaveDatasetButton.configure(state='normal')

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

        self.columnconfigure(0, weight=1)

        Title = ctk.CTkLabel(self, text="Variance threshold", text_color="#FFFFFF", font=LARGEFONT)
        Title.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        EntryFrame = ctk.CTkFrame(self, fg_color="#101010")
        EntryFrame.grid(row=1, column=0, ipadx=0, ipady=0, columnspan=3, sticky="ew")

        EntryFrame.columnconfigure(1, weight=1)

        ThresholdLabel = ctk.CTkLabel(EntryFrame, text="Choose the variance threshold you want:", text_color="#FFFFFF",
                                      font=SMALLFONT)
        ThresholdLabel.grid(row=0, column=0, padx=(0, 4), pady=8)

        ThresholdEntry = ctk.CTkEntry(EntryFrame, width=100, corner_radius=0)
        ThresholdEntry.grid(row=0, column=1, padx=(4, 0), pady=8, sticky="ew")

        ApplyButton = ctk.CTkButton(self, text="Select features",
                                    command=lambda: self.apply_threshold(ThresholdEntry.get(), controller),
                                    corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF",
                                    font=SMALLFONT, hover_color="#F0F0F0", height=48)
        ApplyButton.grid(row=2, column=0, padx=0, pady=(8, 4), sticky="ew")

        CancelButton = ctk.CTkButton(self, text="Cancel", command=lambda: controller.show_frame(BlankPage),
                                     corner_radius=0, text_color="#FFFFFF", bg_color="#101010", fg_color="#fe7b72",
                                     font=SMALLFONT, hover=True, hover_color="#F94545", height=48, width=56)
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

        DATA.file_data = feature_selection_varianceThreshold(DATA.file_data, k)

        DATA.X = DATA.file_data.drop(DATA.target_column, axis=1)
        DATA.y = DATA.file_data[DATA.target_column]

        global app
        app.frames[DataProcessingPage].load_data()

        controller.show_frame(BlankPage)

class KbestfeatPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.configure(fg_color="#101010", width=358)

        self.columnconfigure(0, weight=1)

        Title = ctk.CTkLabel(self, text="K-best features", text_color="#FFFFFF", font=LARGEFONT)
        Title.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        EntryFrame = ctk.CTkFrame(self, fg_color="#101010")
        EntryFrame.grid(row=1, column=0, ipadx=0, ipady=0, sticky="ew")

        EntryFrame.columnconfigure(1, weight=1)

        label = ctk.CTkLabel(EntryFrame,
                             text="Number of features you want to keep\n(Less than the number of actual\nfeatures):",
                             text_color="#FFFFFF", font=SMALLFONT)
        label.grid(row=0, column=0, padx=(0, 4), pady=8, sticky="w")

        KEntry = ctk.CTkEntry(EntryFrame, width=100, corner_radius=0)
        KEntry.grid(row=0, column=1, padx=(4, 0), pady=8, sticky="ew")

        SelectionButton = ctk.CTkButton(self, text="Select features",
                                        command=lambda: self.kbestFeat_Selec_event(KEntry.get(), controller),
                                        corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF",
                                        font=SMALLFONT, hover_color="#F0F0F0", height=48)
        SelectionButton.grid(row=2, column=0, padx=0, pady=(8, 4), sticky="ew")

        CancelButton = ctk.CTkButton(self, text="Cancel", command=lambda: controller.show_frame(BlankPage),
                                     corner_radius=0, text_color="#FFFFFF", bg_color="#101010", fg_color="#fe7b72",
                                     font=SMALLFONT, hover=True, hover_color="#F94545", height=48)
        CancelButton.grid(row=3, column=0, padx=0, pady=4, sticky="ew")

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
        
        DATA.X = DATA.file_data.drop(DATA.target_column, axis=1)
        DATA.y = DATA.file_data[DATA.target_column]

        global app

        app.frames[DataProcessingPage].load_data()
        controller.show_frame(BlankPage)

class MissingValuesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.configure(fg_color="#101010", width=358)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        Title = ctk.CTkLabel(self, text="Missing values", text_color="#FFFFFF", font=LARGEFONT)
        Title.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        self.textbox = ctk.CTkLabel(self, text="", text_color="#FFFFFF", font=SMALLFONT)
        self.textbox.grid(row=1, column=0, padx=0, pady=8, sticky="w")
        
        MeanFillButton = ctk.CTkButton(self, text="Fill with the mean", command=lambda: self.values_handling(controller, method=enums.FillMethod.MEAN), corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=32)
        MeanFillButton.grid(row=2, column=0, padx=0, pady=(8, 4), ipadx=8, ipady=8, sticky="ew")

        MeanFillButton = ctk.CTkButton(self, text="Fill with the mean",
                                       command=lambda: self.values_handling(controller, method=enums.FillMethod.MEAN),
                                       corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF",
                                       font=SMALLFONT, hover_color="#F0F0F0", height=32)
        MeanFillButton.grid(row=2, column=0, padx=0, pady=(8, 4), ipadx=8, ipady=8, sticky="ew")

        MedianFillButton = ctk.CTkButton(self, text="Fill with the median",
                                         command=lambda: self.values_handling(controller,
                                                                              method=enums.FillMethod.MEDIAN),
                                         corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF",
                                         font=SMALLFONT, hover_color="#F0F0F0", height=32)
        MedianFillButton.grid(row=3, column=0, padx=0, pady=4, ipadx=8, ipady=8, sticky="ew")

        RemoveButton = ctk.CTkButton(self, text="Remove rows with missing values",
                                     command=lambda: self.values_handling(controller, method=enums.FillMethod.DROP),
                                     corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF",
                                     font=SMALLFONT, hover_color="#F0F0F0", height=32)
        RemoveButton.grid(row=4, column=0, padx=0, pady=4, ipadx=8, ipady=8, sticky="ew")

        CancelButton = ctk.CTkButton(self, text="Cancel", command=lambda: controller.show_frame(BlankPage),
                                     corner_radius=0, text_color="#FFFFFF", bg_color="#101010", fg_color="#fe7b72",
                                     font=SMALLFONT, hover=True, hover_color="#F94545", height=48, width=56)
        CancelButton.grid(row=5, column=0, padx=0, pady=4, sticky="ew")

    def values_handling(self, controller, value: int | float | str = None,
                        method: enums.FillMethod = enums.FillMethod.MEAN):
        global DATA

        handle_missing_values(DATA.file_data, value, method)
        
        DATA.X = DATA.file_data.drop(DATA.target_column, axis=1)
        DATA.y = DATA.file_data[DATA.target_column]
        
        self.textbox.configure(text = f"Number of missing values: {DATA.file_data.isnull().sum().sum()}\n\nPourcentage of missing values: {(DATA.file_data.isnull().sum().sum() / (DATA.file_data.shape[0] * DATA.file_data.shape[1])) * 100}%")
        
        global app
        app.frames[DataProcessingPage].load_data()
        controller.show_frame(BlankPage)

class DuplicateRowsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.configure(fg_color="#101010", width=358)
        self.columnconfigure(0, weight=1)

        Title = ctk.CTkLabel(self, text="Duplicate Rows", text_color="#FFFFFF", font=LARGEFONT)
        Title.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        self.textbox = ctk.CTkLabel(self, text="", text_color="#FFFFFF", font=SMALLFONT)
        self.textbox.grid(row=1, column=0, pady=8, sticky="w", columnspan=3)

        DropButton = ctk.CTkButton(self, text="Drop duplicate rows",
                                   command=lambda: self.drop_duplicate_rows(controller), corner_radius=0,
                                   text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT,
                                   hover_color="#F0F0F0", height=32)
        DropButton.grid(row=2, column=0, padx=0, pady=(8, 4), ipadx=8, ipady=8, sticky="ew")

        CancelButton = ctk.CTkButton(self, text="Cancel", command=lambda: controller.show_frame(BlankPage),
                                     corner_radius=0, text_color="#FFFFFF", bg_color="#101010", fg_color="#fe7b72",
                                     font=SMALLFONT, hover=True, hover_color="#F94545", height=48)
        CancelButton.grid(row=3, column=0, padx=0, pady=4, sticky="ew")

    def drop_duplicate_rows(self, controller):
        global DATA

        drop_duplicate_rows(DATA.file_data)
        
        self.textbox.configure(text = f"Number of duplicate rows: {DATA.file_data.duplicated().sum()}\n\nPourcentage of duplicate rows: {(DATA.file_data.duplicated().sum() / DATA.file_data.shape[0]) * 100}%")
        
        DATA.X = DATA.file_data.drop(DATA.target_column, axis=1)
        DATA.y = DATA.file_data[DATA.target_column]

        global app
        app.frames[DataProcessingPage].load_data()
        controller.show_frame(BlankPage)

class ConstantFeaturesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.configure(fg_color="#101010", width=358)
        self.columnconfigure(0, weight=1)

        Title = ctk.CTkLabel(self, text="Constant features", text_color="#FFFFFF", font=LARGEFONT)
        Title.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        self.textbox = ctk.CTkLabel(self, text="", text_color="#FFFFFF", font=SMALLFONT)
        self.textbox.grid(row=1, column=0, pady=8, sticky="w")

        DropButton = ctk.CTkButton(self, text="Drop constant columns",
                                   command=lambda: self.drop_contant_columns(controller), corner_radius=0,
                                   text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT,
                                   hover_color="#F0F0F0", height=32)
        DropButton.grid(row=2, column=0, padx=0, pady=(8, 4), ipadx=8, ipady=8, sticky="ew")

        BackButton = ctk.CTkButton(self, text="Cancel", command=lambda: controller.show_frame(BlankPage),
                                   corner_radius=0, text_color="#FFFFFF", bg_color="#101010", fg_color="#fe7b72",
                                   font=SMALLFONT, hover=True, hover_color="#F94545", height=48)
        BackButton.grid(row=3, column=0, padx=0, pady=4, sticky="ew")

    def drop_contant_columns(self, controller):
        global DATA
        
        DATA.file_data = DATA.file_data[get_non_constant_columns(DATA.file_data)]
        
        self.textbox.configure(text = f"Number of constant columns: {len(get_constant_columns(DATA.file_data))}\n\nPourcentage of constant columns: {(len(get_constant_columns(DATA.file_data)) / DATA.file_data.shape[1]) * 100}%")
        
        DATA.X = DATA.file_data.drop(DATA.target_column, axis=1)
        DATA.y = DATA.file_data[DATA.target_column]

        global app
        app.frames[DataProcessingPage].load_data()
        controller.show_frame(BlankPage)

class OutliersPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.configure(fg_color="#101010", width=358)
        self.columnconfigure(0, weight=1)

        Title = ctk.CTkLabel(self, text="Outliers", text_color="#FFFFFF", font=LARGEFONT)
        Title.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        ZScoreDropButton = ctk.CTkButton(self, text="Drop outliers based on z-score",
                                         command=lambda: self.outliers_handling(controller), corner_radius=0,
                                         text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT,
                                         hover_color="#F0F0F0", height=32)
        ZScoreDropButton.grid(row=1, column=0, padx=0, pady=(0, 4), ipadx=8, ipady=8, sticky="ew")

        PercentileDropButton = ctk.CTkButton(self, text="Drop outliers based on percentiles",
                                             command=lambda: self.outliers_handling(controller,
                                                                                    method=enums.OutlierMethod.IQR),
                                             corner_radius=0, text_color="#101010", bg_color="#FFFFFF",
                                             fg_color="#FFFFFF", font=SMALLFONT, hover_color="#F0F0F0", height=32)
        PercentileDropButton.grid(row=2, column=0, padx=0, pady=4, ipadx=8, ipady=8, sticky="ew")

        CancelButton = ctk.CTkButton(self, text="Cancel", command=lambda: controller.show_frame(BlankPage),
                                     corner_radius=0, text_color="#FFFFFF", bg_color="#101010", fg_color="#fe7b72",
                                     font=SMALLFONT, hover=True, hover_color="#F94545", height=48)
        CancelButton.grid(row=3, column=0, padx=0, pady=4, sticky="ew")

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

        Title = ctk.CTkLabel(self, text="Remove columns", text_color="#FFFFFF", font=LARGEFONT)
        Title.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        self.CheckboxesFrame = ctk.CTkScrollableFrame(self, fg_color="#101010")
        self.CheckboxesFrame.grid(row=1, column=0, ipadx=8, ipady=8, pady=8, sticky="ew")

        RemoveButton = ctk.CTkButton(self, text="Remove columns", command=lambda: self.remove_columns(controller),
                                     corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF",
                                     font=SMALLFONT, hover_color="#F0F0F0", height=32)
        RemoveButton.grid(row=2, column=0, padx=0, pady=(8, 4), ipadx=8, ipady=8, sticky="ew")

        CancelButton = ctk.CTkButton(self, text="Cancel", command=lambda: controller.show_frame(BlankPage),
                                     corner_radius=0, text_color="#FFFFFF", bg_color="#101010", fg_color="#fe7b72",
                                     font=SMALLFONT, hover=True, hover_color="#F94545", height=48)
        CancelButton.grid(row=3, column=0, padx=0, pady=4, sticky="ew")

    def load_checkboxes(self):
        self.df_columns = get_dataframe_columns(DATA.X)
        
        for checkbutton in self.CheckboxesFrame.winfo_children():
            checkbutton.destroy()

        self.checkbuttons_vars = [tk.BooleanVar() for value in self.df_columns]

        self.checkbuttons = []
        for index, value in enumerate(self.df_columns):
            self.checkbutton = ctk.CTkCheckBox(self.CheckboxesFrame, text=value, variable=self.checkbuttons_vars[index],
                                               text_color="#FFFFFF", corner_radius=0, font=SMALLFONT,
                                               border_color="#F0F0F0", hover_color="#F0F0F0", fg_color="#FFFFFF")
            self.checkbutton.pack(side="top", anchor="center", expand=True, fill="both", padx=0, pady=4)
            self.checkbuttons.append(self.checkbutton)

    def remove_columns(self, controller):
        global DATA
        
        self.selected_values = [value for value, var in zip(self.df_columns, self.checkbuttons_vars) if var.get()]

        DATA.file_data.drop(self.selected_values, axis=1, inplace=True)

        DATA.X = DATA.file_data.drop(DATA.target_column, axis=1)
        DATA.y = DATA.file_data[DATA.target_column]

        global app

        app.frames[DataProcessingPage].TargetColumnCombobox.configure(values=get_dataframe_columns(DATA.file_data))
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

        Title = ctk.CTkLabel(self, text="Label encoding", text_color="#FFFFFF", font=LARGEFONT)
        Title.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        self.optionmenu_var2 = ctk.StringVar(value="Column X")
        self.ColumnsCombobox = ctk.CTkOptionMenu(master=self,
                                                 values=[],
                                                 command=lambda x: self.Column_choice_handler(x, controller),
                                                 variable=self.optionmenu_var2,
                                                 width=150,
                                                 corner_radius=0, text_color="#101010", bg_color="#FFFFFF",
                                                 fg_color="#FFFFFF", font=SMALLFONT, height=32, button_color="#FFFFFF",
                                                 button_hover_color="#FFFFFF", dropdown_font=SMALLFONT,
                                                 dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF",
                                                 dropdown_text_color="#101010")

        self.ColumnsCombobox.grid(row=1, column=0, padx=0, pady=(8, 4), ipadx=8, ipady=8, sticky="ew")

        CancelButton = ctk.CTkButton(self, text="Cancel", command=lambda: controller.show_frame(BlankPage),
                                     corner_radius=0, text_color="#FFFFFF", bg_color="#101010", fg_color="#fe7b72",
                                     font=SMALLFONT, hover=True, hover_color="#F94545", height=48)
        CancelButton.grid(row=2, column=0, padx=0, pady=4, sticky="ew")

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
        
        BackImage = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((24, 24), Image.LANCZOS))
        # prepare data
        self.visPlotType = None
        self.visColumnX = None
        self.visColumnY = None

        Title = ctk.CTkLabel(self, text="Visualization", text_color="#FFFFFF", font=LARGEFONT)
        Title.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        ButtonsFrame = ctk.CTkFrame(self, fg_color="#101010")
        ButtonsFrame.grid(row=1, column=0, ipadx=0, ipady=0, columnspan=3, sticky="ew")

        CancelButton = ctk.CTkButton(ButtonsFrame, image=BackImage, text="",
                                     command=lambda: controller.show_frame(DataProcessingPage),
                                     corner_radius=0, text_color="#FFFFFF", bg_color="#101010", fg_color="#fe7b72",
                                     font=SMALLFONT, hover=True, hover_color="#F94545", height=48, width=56)
        CancelButton.grid(row=0, column=0, padx=(0, 4), pady=8, sticky="w")

        self.PlotTypeOptionmenuVar = ctk.StringVar(value="Plot type")
        self.PlotTypeCombobox = ctk.CTkOptionMenu(master=ButtonsFrame,
                                                  values=["Scatter plot", "Histogram", "Bar chart", "Line chart",
                                                          "Box plot"],
                                                  command=lambda x: self.plotType_optionmenu_callback(x),
                                                  variable=self.PlotTypeOptionmenuVar,
                                                  width=150, corner_radius=0, text_color="#101010", bg_color="#FFFFFF",
                                                  fg_color="#FFFFFF", font=SMALLFONT, height=32, button_color="#FFFFFF",
                                                  button_hover_color="#FFFFFF", dropdown_font=SMALLFONT,
                                                  dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF",
                                                  dropdown_text_color="#101010")
        self.PlotTypeCombobox.grid(row=0, column=3, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        self.ColumnXOptionmenuVar = ctk.StringVar(value="Column X")
        self.ColumnXCombobox = ctk.CTkOptionMenu(master=ButtonsFrame,
                                                 values=[],
                                                 command=lambda x: self.columnX_optionmenu_callback(x),
                                                 variable=self.ColumnXOptionmenuVar,
                                                 width=150, state='disabled', corner_radius=0, text_color="#101010",
                                                 bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=32,
                                                 button_color="#FFFFFF", button_hover_color="#FFFFFF",
                                                 dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0",
                                                 dropdown_fg_color="#FFFFFF", dropdown_text_color="#101010")
        self.ColumnXCombobox.grid(row=0, column=4, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        self.ColumnYOptionmenuVar = ctk.StringVar(value="Column Y")
        self.ColumnYCombobox = ctk.CTkOptionMenu(master=ButtonsFrame,
                                                 values=[],
                                                 command=lambda x: self.columnY_optionmenu_callback(x),
                                                 variable=self.ColumnYOptionmenuVar,
                                                 width=150, state='disabled', corner_radius=0, text_color="#101010",
                                                 bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=32,
                                                 button_color="#FFFFFF", button_hover_color="#FFFFFF",
                                                 dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0",
                                                 dropdown_fg_color="#FFFFFF", dropdown_text_color="#101010")
        self.ColumnYCombobox.grid(row=0, column=5, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        BinsNbrLabel = ctk.CTkLabel(ButtonsFrame, text="Bins number:", text_color="#FFFFFF", font=SMALLFONT)
        BinsNbrLabel.grid(row=0, column=6, padx=0, pady=8, sticky="w")

        self.BinsEntry = ctk.CTkEntry(ButtonsFrame, width=100, state='disabled')
        self.BinsEntry.grid(row=0, column=7, padx=8, pady=8)

        MarkerSizeLabel = ctk.CTkLabel(ButtonsFrame, text="Marker size:", text_color="#FFFFFF", font=SMALLFONT)
        MarkerSizeLabel.grid(row=0, column=8, padx=0, pady=8, sticky="w")

        self.MarkerSizeEntry = ctk.CTkEntry(ButtonsFrame, width=100, state='disabled')
        self.MarkerSizeEntry.grid(row=0, column=9, padx=8, pady=8)

        PlotButton = ctk.CTkButton(ButtonsFrame, text="Plot", command=lambda: self.plot(self.BinsEntry.get()),
                                   corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF",
                                   font=SMALLFONT, hover_color="#F0F0F0", height=32)
        PlotButton.grid(row=0, column=10, padx=4, pady=8, ipadx=8, ipady=8, sticky="w")

        PlotFrame = ctk.CTkFrame(self, fg_color="#101010")
        PlotFrame.grid(row=2, column=0, columnspan=5, ipadx=8, ipady=8, sticky="nsew")

        self.figure = Figure(dpi=100)

        # create FigureCanvasTkAgg object
        self.figure_canvas = FigureCanvasTkAgg(self.figure, PlotFrame)
        self.figure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # create the toolbar
        self.toolbar = NavigationToolbar2Tk(self.figure_canvas, PlotFrame)
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
            self.MarkerSizeEntry.configure(state="normal")
            self.BinsEntry.configure(state="disabled")
            self.ColumnXCombobox.configure(state="normal")
            self.ColumnYCombobox.configure(state="normal")
        elif self.visPlotType == "Histogram":
            self.MarkerSizeEntry.configure(state="disabled")
            self.BinsEntry.configure(state="normal")
            self.ColumnXCombobox.configure(state="normal")
            self.ColumnYCombobox.configure(state="disabled")
        elif self.visPlotType == "Bar chart":
            self.MarkerSizeEntry.configure(state="disabled")
            self.BinsEntry.configure(state="disabled")
            self.ColumnXCombobox.configure(state="normal")
            self.ColumnYCombobox.configure(state="normal")
        elif self.visPlotType == "Line chart":
            self.MarkerSizeEntry.configure(state="disabled")
            self.BinsEntry.configure(state="disabled")
            self.ColumnXCombobox.configure(state="normal")
            self.ColumnYCombobox.configure(state="normal")
        elif self.visPlotType == "Box plot":
            self.MarkerSizeEntry.configure(state="disabled")
            self.BinsEntry.configure(state="disabled")
            self.ColumnXCombobox.configure(state="normal")
            self.ColumnYCombobox.configure(state="disabled")

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
            
            if self.MarkerSizeEntry.get() == '' or self.MarkerSizeEntry.get() == None:
                MarkerSize = 5
            else:
                try:
                    MarkerSize = int(self.MarkerSizeEntry.get())
                except ValueError:
                    MarkerSize = 5

            self.axes.scatter(DATA.file_data[self.visColumnX], DATA.file_data[self.visColumnY], s=MarkerSize, alpha=0.5)
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

        Title = ctk.CTkLabel(self, text="Save dataset", text_color="#FFFFFF", font=LARGEFONT)
        Title.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        EntryFrame = ctk.CTkFrame(self, fg_color="#101010")
        EntryFrame.grid(row=1, column=0, ipadx=0, ipady=0, columnspan=3, sticky="ew")

        EntryFrame.columnconfigure(1, weight=1)

        EntryLabel = ctk.CTkLabel(EntryFrame, text="File name:", text_color="#FFFFFF", font=SMALLFONT)
        EntryLabel.grid(row=0, column=0, padx=(0, 10), pady=8, sticky="w")

        self.FileNameEntry = ctk.CTkEntry(EntryFrame, width=100, height=24, corner_radius=0)
        self.FileNameEntry.grid(row=0, column=1, padx=(8, 0), pady=8, sticky="ew")

        ChooseDirButton = ctk.CTkButton(self, text="Choose directory", command=lambda: self.SelectSaveDirectory(),
                                        corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF",
                                        font=SMALLFONT, hover_color="#F0F0F0", height=48, width=56)
        ChooseDirButton.grid(row=2, column=0, padx=0, pady=(8, 4), sticky="ew")

        SaveFileButton = ctk.CTkButton(self, text="Save file", command=lambda: self.SaveFile(controller),
                                       corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF",
                                       font=SMALLFONT, hover_color="#F0F0F0", height=48, width=56)
        SaveFileButton.grid(row=3, column=0, padx=0, pady=4, sticky="ew")

        CancelButton = ctk.CTkButton(self, text="Cancel", command=lambda: controller.show_frame(BlankPage),
                                     corner_radius=0, text_color="#FFFFFF", bg_color="#101010", fg_color="#fe7b72",
                                     font=SMALLFONT, hover=True, hover_color="#F94545", height=48, width=56)
        CancelButton.grid(row=4, column=0, padx=0, pady=4, sticky="ew")

    def SelectSaveDirectory(self):
        self.SaveDirectory = ctk.filedialog.askdirectory()
    
    def SaveFile(self, controller):
        global DATA
        
        if hasattr(self, 'SaveDirectory'):
            if self.SaveDirectory == None or self.SaveDirectory == '':
                tk.messagebox.showerror("Information", "Please select a directory")
                return
            elif self.FileNameEntry.get() == None or self.FileNameEntry.get() == '':
                tk.messagebox.showerror("Information", "Please enter a file name")
                return
            
            DATA.file_data.to_excel(self.SaveDirectory + "/" + self.FileNameEntry.get() + ".xlsx", index=False)

            controller.show_frame(BlankPage)

        else:
            tk.messagebox.showerror("Information", "Please select a directory")
            return

class DataSplitPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        BackImage = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((24, 24), Image.LANCZOS))
        continueImg = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").rotate(180).resize((24, 24), Image.LANCZOS))

        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)

        Title = ctk.CTkLabel(self, text="Data splitting", text_color="#FFFFFF", font=LARGEFONT)
        Title.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        ButtonsFrame = ctk.CTkFrame(self, fg_color="#101010")
        ButtonsFrame.grid(row=1, column=0, ipadx=0, ipady=0, columnspan=3, sticky="ew")

        BackButton = ctk.CTkButton(ButtonsFrame, image=BackImage, text="",
                                   command=lambda: controller.show_frame(DataProcessingPage), corner_radius=0,
                                   text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT,
                                   hover_color="#F0F0F0", height=48, width=56)
        BackButton.grid(row=0, column=0, padx=(0, 4), pady=8, sticky="w")

        SplitDataButton = ctk.CTkButton(ButtonsFrame, text="Split data",
                                        command=lambda: self.split_train_test(RatioEntry.get(), RandomStateEntry.get()),
                                        corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF",
                                        font=SMALLFONT, hover_color="#F0F0F0", height=48, width=86)
        SplitDataButton.grid(row=0, column=1, padx=4, pady=8, sticky="w")

        ContinueButton = ctk.CTkButton(ButtonsFrame, image=continueImg, text="",
                                       command=lambda: self.mlPage_switch(controller), corner_radius=0,
                                       text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT,
                                       hover_color="#F0F0F0", height=48, width=56)
        ContinueButton.grid(row=0, column=2, padx=4, pady=8, sticky="w")

        RatioEntryFrame = ctk.CTkFrame(self, fg_color="#101010")
        RatioEntryFrame.grid(row=2, column=0, ipadx=0, ipady=0, columnspan=3, sticky="ew")

        RatioLabel = ctk.CTkLabel(RatioEntryFrame, text="Test data ratio(default: 0.2):", text_color="#FFFFFF",
                                  font=SMALLFONT)
        RatioLabel.grid(row=0, column=0, padx=(0, 8), pady=8, sticky="w")

        RatioEntry = ctk.CTkEntry(RatioEntryFrame, width=100, height=24)
        RatioEntry.grid(row=0, column=1, padx=8)

        RandomStateEntryFrame = ctk.CTkFrame(self, fg_color="#101010")
        RandomStateEntryFrame.grid(row=3, column=0, ipadx=0, ipady=0, columnspan=3, sticky="ew")

        RandomStateLabel = ctk.CTkLabel(RandomStateEntryFrame, text="Random state(default: 42):", text_color="#FFFFFF",
                                        font=SMALLFONT)
        RandomStateLabel.grid(row=0, column=0, padx=(0, 8), pady=8, sticky="w")

        RandomStateEntry = ctk.CTkEntry(RandomStateEntryFrame, width=100, height=24)
        RandomStateEntry.grid(row=0, column=1, padx=8)

        SheetsFrame = ctk.CTkFrame(self, fg_color="#101010")
        SheetsFrame.grid(row=4, column=0, columnspan=3, sticky="nsew")

        SheetsFrame.columnconfigure(0, weight=1)
        SheetsFrame.columnconfigure(1, weight=1)

        SheetsFrame.rowconfigure(0, weight=1)

        TrainFrame = ctk.CTkFrame(SheetsFrame, fg_color="#101010")
        TrainFrame.grid(row=0, column=0, padx=(0, 12), sticky="nsew")

        TestFrame = ctk.CTkFrame(SheetsFrame, fg_color="#101010")
        TestFrame.grid(row=0, column=1, padx=(12, 0), sticky="nsew")

        TrainLabel = ctk.CTkLabel(TrainFrame, text="Training data", pady=24, text_color="#FFFFFF", font=LARGEFONT)
        TrainLabel.pack(side="top", fill="both")

        self.TrainSheet = Sheet(TrainFrame, data=None)
        self.TrainSheet.enable_bindings()
        self.TrainSheet.pack(side="top" , fill="both", expand=True)

        TestLabel = ctk.CTkLabel(TestFrame, text="Testing data", pady=24, text_color="#FFFFFF", font=LARGEFONT)
        TestLabel.pack(side="top", fill="both")

        self.TestSheet = Sheet(TestFrame, data=None)
        self.TestSheet.enable_bindings()
        self.TestSheet.pack(side="top" , fill="both", expand=True)

    def split_train_test(self, k='', random_state=''):
        global app
        global DATA
        
        if (k != '' and k != None) and (random_state != '' and random_state != None):
            try:
                k = float(k)
                random_state = int(random_state)

                if k <= 0 or k >= 1:
                    tk.messagebox.  showerror("Value", "The value you chose for k is invalid")
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
        
        self.TrainSheet.set_sheet_data(data = concat([DATA.X_train, DATA.y_train], axis=1).values.tolist())
        self.TestSheet.set_sheet_data(data = concat([DATA.X_test, DATA.y_test], axis=1).values.tolist())
    
    def mlPage_switch(self, controller):
        global app
        global DATA

        """ if DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None or DATA.X is None or DATA.y is None:
            tk.messagebox.showerror("Information", "Please split the data first")
            return """

        app.frames[MLPage].Title.configure(text=DATA.mlModelType)
        controller.show_frame(MLPage)

class MLPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        BackImage = ImageTk.PhotoImage(Image.open("./assets/icons/back.png").resize((24, 24), Image.LANCZOS))

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        self.Title = ctk.CTkLabel(self, text="Machine learning", text_color="#FFFFFF", font=LARGEFONT)
        self.Title.grid(row=0, column=0, padx=0, pady=8, sticky="w")

        self.ButtonsFrame = ctk.CTkFrame(self, fg_color="#101010")
        self.ButtonsFrame.grid(row=1, column=0, ipadx=0, ipady=0, columnspan=3, sticky="ew")

        BackButton = ctk.CTkButton(self.ButtonsFrame, image=BackImage, text="",
                                   command=lambda: controller.show_frame(DataSplitPage), corner_radius=0,
                                   text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT,
                                   hover_color="#F0F0F0", height=48, width=56)
        BackButton.grid(row=0, column=0, padx=(0, 4), pady=8, sticky="w")

        self.ModelTypeOptionmenuVar = ctk.StringVar(value="Model type")
        self.ModelTypeCombobox = ctk.CTkOptionMenu(master=self.ButtonsFrame,
                                                   values=["Linear Regression", "Logistic Regression", "Decision Tree",
                                                           "Naive Bayes", "Random Forest", "K-Nearest Neighbors (KNN)",
                                                           "K-means", "Support Vector Machine (SVM)"],
                                                   command=lambda x: self.optionmenu_callback(x),
                                                   width=250,
                                                   variable=self.ModelTypeOptionmenuVar,
                                                   corner_radius=0, text_color="#101010", bg_color="#FFFFFF",
                                                   fg_color="#FFFFFF", font=SMALLFONT, height=48,
                                                   button_color="#FFFFFF", button_hover_color="#FFFFFF",
                                                   dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0",
                                                   dropdown_fg_color="#FFFFFF", dropdown_text_color="#101010")
        self.ModelTypeCombobox.grid(row=0, column=1, padx=4, pady=8, sticky="w")

        self.TrainButton = ctk.CTkButton(self.ButtonsFrame, text="Train model", command=lambda: self.train_mlModel(),
                                    corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF",
                                    font=SMALLFONT, hover_color="#F0F0F0", height=48, state="disabled")
        self.TrainButton.grid(row=0, column=2, padx=4, pady=8, sticky="w")

        self.TestButton = ctk.CTkButton(self.ButtonsFrame, text="Test model", command=lambda: self.test_mlModel(),
                                        corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF",
                                        font=SMALLFONT, hover_color="#F0F0F0", height=48, state="disabled")
        self.TestButton.grid(row=0, column=3, padx=4, pady=8, sticky="w")

        self.SaveModelButton = ctk.CTkButton(self.ButtonsFrame, text="Save model",
                                             command=lambda: self.openSaveModelWindow(), corner_radius=0,
                                             text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF",
                                             font=SMALLFONT, hover_color="#F0F0F0", height=48, state="disabled")
        self.SaveModelButton.grid(row=0, column=4, padx=4, pady=8, sticky="w")

        self.showMetricsPlotsBtn = ctk.CTkButton(self.ButtonsFrame, text="Show classification metrics plots",
                                                 command=lambda: self.showMetricsPlots(), corner_radius=0,
                                                 text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF",
                                                 font=SMALLFONT, hover_color="#F0F0F0", height=48, state="disabled")
        self.showMetricsPlotsBtn.grid(row=0, column=5, padx=4, pady=8, sticky="w")

        self.ImportModelButton = ctk.CTkButton(self.ButtonsFrame, text="Import a model",
                                                 command=lambda: self.importModelHandler(), corner_radius=0,
                                                 text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF",
                                                 font=SMALLFONT, hover_color="#F0F0F0", height=48)
        self.ImportModelButton.grid(row=0, column=6, padx=4, pady=8, sticky="w")

        self.ModelConfigFrame = ctk.CTkFrame(self, fg_color="#101010", height=48)
        self.ModelConfigFrame.grid(row=2, column=0, pady=(1, 8), sticky="nsew")

        self.MetricsFrame = ctk.CTkFrame(self, fg_color="#101010")
        self.MetricsFrame.grid(row=3, column=0, pady=0, sticky="nsew")
        
        self.rowconfigure(3, weight=1)
        self.MetricsFrame.columnconfigure(1, weight=1)
        self.MetricsFrame.columnconfigure(2, weight=1)
        self.MetricsFrame.rowconfigure(0, weight=1)

        self.NumericMetricsFrame = ctk.CTkFrame(self.MetricsFrame, fg_color="#101010")
        self.NumericMetricsFrame.grid(row=0, column=0, sticky="nsew")

        self.ConfusionMatrixFrame = ctk.CTkFrame(self.MetricsFrame, fg_color="#101010")
        self.ConfusionMatrixFrame.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        self.ROCCurveFrame = ctk.CTkFrame(self.MetricsFrame, fg_color="#101010")
        self.ROCCurveFrame.grid(row=0, column=2, padx=0, sticky="nsew")

    def optionmenu_callback(self, choice: str):
        global DATA

        target_type = DATA.y.dtype.name

        if (target_type != 'int64' and target_type != 'float64' and target_type != 'int32' and target_type != 'float32' and choice in ["Linear Regression", "K-means"]) or ((target_type == 'float64' or target_type == 'float32') and choice not in ["Linear Regression", "Decision tree", "K-means"]):
            tk.messagebox.showerror("Information", "Please choose a valid model for your chosen target column")
            return
        
        DATA.mlModelType = choice
        
        for widget in self.ModelConfigFrame.winfo_children():
            widget.destroy()

        for widget in self.NumericMetricsFrame.winfo_children():
            widget.destroy()

        for widget in self.ConfusionMatrixFrame.winfo_children():
            widget.destroy()

        for widget in self.ROCCurveFrame.winfo_children():
            widget.destroy()

        if choice == 'Linear Regression':
            self.showMetricsPlotsBtn.configure(state="disabled")

            self.MetricsFrame.columnconfigure(2, weight=1)
            
        elif choice == 'Naive Bayes':
            DisributionLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Distribution:", text_color="#FFFFFF",
                                            font=SMALLFONT)
            DisributionLabel.grid(row=0, column=0, padx=(0, 4), sticky="w")

            self.DistributionVar = ctk.StringVar(value="Gaussian")
            self.nbDistributionBox = ctk.CTkOptionMenu(master=self.ModelConfigFrame,
                                                       values=["Gaussian", "Multinomial", "Bernoulli"],
                                                       width=250,
                                                       variable=self.DistributionVar,
                                                       corner_radius=0, text_color="#101010", bg_color="#FFFFFF",
                                                       fg_color="#FFFFFF", font=SMALLFONT, height=48,
                                                       button_color="#FFFFFF", button_hover_color="#FFFFFF",
                                                       dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0",
                                                       dropdown_fg_color="#FFFFFF", dropdown_text_color="#101010")
            self.nbDistributionBox.grid(row=0, column=1, padx=4, pady=0, sticky="w")
            
            self.MetricsFrame.columnconfigure(2, weight=1)

        elif choice == 'Decision Tree':
            CriterionLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Criterion:", text_color="#FFFFFF",
                                          font=SMALLFONT)
            CriterionLabel.grid(row=0, column=0, padx=(0, 4), pady=4, sticky="w")

            self.optionmenu_var2 = ctk.StringVar(value="gini")
            self.dtCriterionBox = ctk.CTkOptionMenu(master=self.ModelConfigFrame,
                                                    values=["gini", "entropy", "log_loss"],
                                                    width=250,
                                                    command=lambda x: print(x),
                                                    variable=self.optionmenu_var2,
                                                    corner_radius=0, text_color="#101010", bg_color="#FFFFFF",
                                                    fg_color="#FFFFFF", font=SMALLFONT, height=48,
                                                    button_color="#FFFFFF", button_hover_color="#FFFFFF",
                                                    dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0",
                                                    dropdown_fg_color="#FFFFFF", dropdown_text_color="#101010")
            self.dtCriterionBox.grid(row=0, column=1, padx=4, pady=0, sticky="w")

            MaxDepthLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Max depth:", text_color="#FFFFFF", font=SMALLFONT)
            MaxDepthLabel.grid(row=0, column=3, padx=(0, 4), sticky="w")

            self.dtMaxDepthEntry = ctk.CTkEntry(self.ModelConfigFrame, width=100, height=24)
            self.dtMaxDepthEntry.grid(row=0, column=4, padx=4, sticky="w")

            MinSamplesSplitLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Min samples split:", text_color="#FFFFFF",
                                                font=SMALLFONT)
            MinSamplesSplitLabel.grid(row=0, column=5, padx=(0, 4), sticky="w")

            self.dtMinSamplesSplitEntry = ctk.CTkEntry(self.ModelConfigFrame, width=100, height=24)
            self.dtMinSamplesSplitEntry.grid(row=0, column=6, padx=4, sticky="w")
            
            RandomStateLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Random state:", text_color="#FFFFFF", font=SMALLFONT)
            RandomStateLabel.grid(row=0, column=7, padx=(0, 4), sticky="w")

            self.dtRandomStateEntry = ctk.CTkEntry(self.ModelConfigFrame, width=100, height=24)
            self.dtRandomStateEntry.grid(row=0, column=8, padx=4, sticky="w")

            self.MetricsFrame.columnconfigure(2, weight=1)

        elif choice == 'Logistic Regression':
            SolverLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Solver:", text_color="#FFFFFF", font=SMALLFONT)
            SolverLabel.grid(row=0, column=0, padx=(0, 4), sticky="w")

            self.SolverVar = ctk.StringVar(value="lbfgs")
            self.lrSolverBox = ctk.CTkOptionMenu(master=self.ModelConfigFrame,
                                                 values=["lbfgs", "liblinear", "sag", "saga", 'newton-cg',
                                                         'newton-cholesky'],
                                                 width=250,
                                                 variable=self.SolverVar,
                                                 corner_radius=0, text_color="#101010", bg_color="#FFFFFF",
                                                 fg_color="#FFFFFF", font=SMALLFONT, height=48, button_color="#FFFFFF",
                                                 button_hover_color="#FFFFFF", dropdown_font=SMALLFONT,
                                                 dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF",
                                                 dropdown_text_color="#101010")
            self.lrSolverBox.grid(row=0, column=1, padx=4, pady=0, sticky="w")

            PenaltyLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Penalty:", text_color="#FFFFFF", font=SMALLFONT)
            PenaltyLabel.grid(row=0, column=2, padx=(0, 4), sticky="w")

            self.PenaltyVar = ctk.StringVar(value="l2")
            self.lrPenaltyBox = ctk.CTkOptionMenu(master=self.ModelConfigFrame,
                                                  values=["l1", "l2", "elasticnet", "none"],
                                                  width=250,
                                                  variable=self.PenaltyVar,
                                                  corner_radius=0, text_color="#101010", bg_color="#FFFFFF",
                                                  fg_color="#FFFFFF", font=SMALLFONT, height=48, button_color="#FFFFFF",
                                                  button_hover_color="#FFFFFF", dropdown_font=SMALLFONT,
                                                  dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF",
                                                  dropdown_text_color="#101010")
            self.lrPenaltyBox.grid(row=0, column=3, padx=4, sticky="w")

            CLabel = ctk.CTkLabel(self.ModelConfigFrame, text="C:", text_color="#FFFFFF", font=SMALLFONT)
            CLabel.grid(row=0, column=4, padx=(0, 4), sticky="w")

            self.lrCEntry = ctk.CTkEntry(self.ModelConfigFrame, width=100, height=24)
            self.lrCEntry.grid(row=0, column=5, padx=4, sticky="w")

            MaxIterLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Max iter:", text_color="#FFFFFF", font=SMALLFONT)
            MaxIterLabel.grid(row=0, column=6, padx=(0, 4), sticky="w")

            self.lrMaxIterEntry = ctk.CTkEntry(self.ModelConfigFrame, width=100, height=24)
            self.lrMaxIterEntry.grid(row=0, column=7, padx=4, sticky="w")
            
            RandomStateLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Random state:", text_color="#FFFFFF", font=SMALLFONT)
            RandomStateLabel.grid(row=0, column=8, padx=(0, 4), sticky="w")

            self.lrRandomStateEntry = ctk.CTkEntry(self.ModelConfigFrame, width=100, height=24)
            self.lrRandomStateEntry.grid(row=0, column=9, padx=4, sticky="w")

            self.MetricsFrame.columnconfigure(2, weight=1)

        elif choice == 'Random Forest':
            CriterionLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Criterion:", text_color="#FFFFFF", font=SMALLFONT)
            CriterionLabel.grid(row=0, column=0, padx=(0, 4), sticky="w")

            self.CriterionVar = ctk.StringVar(value="gini")
            self.rfCriterionBox = ctk.CTkOptionMenu(master=self.ModelConfigFrame,
                                                    values=["gini", "entropy"],
                                                    width=250,
                                                    variable=self.CriterionVar,
                                                    corner_radius=0, text_color="#101010", bg_color="#FFFFFF",
                                                    fg_color="#FFFFFF", font=SMALLFONT, height=48,
                                                    button_color="#FFFFFF", button_hover_color="#FFFFFF",
                                                    dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0",
                                                    dropdown_fg_color="#FFFFFF", dropdown_text_color="#101010")
            self.rfCriterionBox.grid(row=0, column=1, padx=4, pady=0, sticky="w")

            MaxDepthLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Max depth:", text_color="#FFFFFF", font=SMALLFONT)
            MaxDepthLabel.grid(row=0, column=3, padx=(0, 4), sticky="w")

            self.rfMaxDepthEntry = ctk.CTkEntry(self.ModelConfigFrame, width=100, height=24)
            self.rfMaxDepthEntry.grid(row=0, column=4, padx=4, sticky="w")

            MinSamplesSplitLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Min samples split:", text_color="#FFFFFF", font=SMALLFONT)
            MinSamplesSplitLabel.grid(row=0, column=5, padx=(0, 4), sticky="w")

            self.rfMinSamplesSplitEntry = ctk.CTkEntry(self.ModelConfigFrame, width=100, height=24)
            self.rfMinSamplesSplitEntry.grid(row=0, column=6, padx=4, sticky="w")
            
            RandomStateLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Random state:", text_color="#FFFFFF", font=SMALLFONT)
            RandomStateLabel.grid(row=0, column=7, padx=(0, 4), sticky="w")

            self.rfRandomStateEntry = ctk.CTkEntry(self.ModelConfigFrame, width=100, height=24)
            self.rfRandomStateEntry.grid(row=0, column=8, padx=4, sticky="w")

            self.MetricsFrame.columnconfigure(2, weight=1)

        elif choice == 'K-Nearest Neighbors (KNN)':
            NNeighborsLabel = ctk.CTkLabel(self.ModelConfigFrame, text="N neighbors:", text_color="#FFFFFF", font=SMALLFONT)
            NNeighborsLabel.grid(row=0, column=0, padx=(0, 4), sticky="w")

            self.knnNNeighborsEntry = ctk.CTkEntry(self.ModelConfigFrame, width=100, height=24)
            self.knnNNeighborsEntry.grid(row=0, column=1, padx=4, sticky="w")

            AlgorithmLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Algorithm:", text_color="#FFFFFF", font=SMALLFONT)
            AlgorithmLabel.grid(row=0, column=2, padx=(0, 4), sticky="w")

            self.AlgorithmVar = ctk.StringVar(value="auto")
            self.knnAlgorithmBox = ctk.CTkOptionMenu(master=self.ModelConfigFrame,
                                                     values=["auto", "ball_tree", "kd_tree", "brute"],
                                                     width=250,
                                                     variable=self.AlgorithmVar,
                                                     corner_radius=0, text_color="#101010", bg_color="#FFFFFF",
                                                     fg_color="#FFFFFF", font=SMALLFONT, height=48,
                                                     button_color="#FFFFFF", button_hover_color="#FFFFFF",
                                                     dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0",
                                                     dropdown_fg_color="#FFFFFF", dropdown_text_color="#101010")
            self.knnAlgorithmBox.grid(row=0, column=3, padx=4, pady=0, sticky="w")

            LeafSizeLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Leaf size:", text_color="#FFFFFF", font=SMALLFONT)
            LeafSizeLabel.grid(row=0, column=4, padx=(0, 4), sticky="w")

            self.knnLeafSizeEntry = ctk.CTkEntry(self.ModelConfigFrame, width=100, height=24)
            self.knnLeafSizeEntry.grid(row=0, column=5, padx=4, sticky="w")
            
            MetricLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Metric:", text_color="#FFFFFF", font=SMALLFONT)
            MetricLabel.grid(row=0, column=6, padx=(0, 4), sticky="w")

            self.optionmenu_var2 = ctk.StringVar(value="minkowski")
            self.knnMetricBox = ctk.CTkOptionMenu(master=self.ModelConfigFrame,
                                                  values=["euclidean", "manhattan", "chebyshev", "minkowski",
                                                          "wminkowski", "seuclidean", "mahalanobis"],
                                                  width=250,
                                                  variable=self.optionmenu_var2,
                                                  corner_radius=0, text_color="#101010", bg_color="#FFFFFF",
                                                  fg_color="#FFFFFF", font=SMALLFONT, height=48, button_color="#FFFFFF",
                                                  button_hover_color="#FFFFFF", dropdown_font=SMALLFONT,
                                                  dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF",
                                                  dropdown_text_color="#101010")
            self.knnMetricBox.grid(row=0, column=7, padx=4, pady=0, sticky="w")

            self.MetricsFrame.columnconfigure(2, weight=1)

        elif choice == 'K-means':
            NClustersLabel = ctk.CTkLabel(self.ModelConfigFrame, text="N clusters:", text_color="#FFFFFF",
                                          font=SMALLFONT)
            NClustersLabel.grid(row=0, column=0, padx=(0, 4), sticky="w")

            self.kmNClustersEntry = ctk.CTkEntry(self.ModelConfigFrame, width=100, height=24)
            self.kmNClustersEntry.grid(row=0, column=1, padx=4, sticky="w")

            MaxIterLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Max iter:", text_color="#FFFFFF", font=SMALLFONT)
            MaxIterLabel.grid(row=0, column=3, padx=(0, 4), sticky="w")

            self.kmMaxIterEntry = ctk.CTkEntry(self.ModelConfigFrame, width=100, height=24)
            self.kmMaxIterEntry.grid(row=0, column=4, padx=4, sticky="w")

            AlgorithmLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Algorithm:", text_color="#FFFFFF", font=SMALLFONT)
            AlgorithmLabel.grid(row=0, column=5, padx=(0, 4), sticky="w")

            self.AlgorithmVar = ctk.StringVar(value="lloyd")
            self.kmAlgorithmBox = ctk.CTkOptionMenu(master=self.ModelConfigFrame,
                                                    values=["lloyd", "full", "elkan"],
                                                    width=250,
                                                    variable=self.AlgorithmVar,
                                                    corner_radius=0, text_color="#101010", bg_color="#FFFFFF",
                                                    fg_color="#FFFFFF", font=SMALLFONT, height=48,
                                                    button_color="#FFFFFF", button_hover_color="#FFFFFF",
                                                    dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0",
                                                    dropdown_fg_color="#FFFFFF", dropdown_text_color="#101010")
            self.kmAlgorithmBox.grid(row=0, column=6, padx=4, pady=0, sticky="w")

            RandomStateLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Random state:", text_color="#FFFFFF",
                                            font=SMALLFONT)
            RandomStateLabel.grid(row=0, column=7, padx=(0, 4), sticky="w")

            self.kmRandomStateEntry = ctk.CTkEntry(self.ModelConfigFrame, width=100, height=24)
            self.kmRandomStateEntry.grid(row=0, column=8, padx=4, sticky="w")

            self.MetricsFrame.columnconfigure(2, weight=0)

        elif choice == 'Support Vector Machine (SVM)':
            CLabel = ctk.CTkLabel(self.ModelConfigFrame, text="C:", text_color="#FFFFFF", font=SMALLFONT)
            CLabel.grid(row=0, column=0, padx=(0, 4), sticky="w")

            self.svmCEntry = ctk.CTkEntry(self.ModelConfigFrame, width=100, height=24)
            self.svmCEntry.grid(row=0, column=1, padx=4, sticky="w")

            KernelLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Kernel:", text_color="#FFFFFF", font=SMALLFONT)
            KernelLabel.grid(row=0, column=3, padx=(0, 4), sticky="w")

            self.KernelVar = ctk.StringVar(value="rbf")
            self.svmKernelBox = ctk.CTkOptionMenu(master=self.ModelConfigFrame,
                                                  values=["linear", "poly", "rbf", "sigmoid", "precomputed"],
                                                  width=250,
                                                  variable=self.KernelVar,
                                                  corner_radius=0, text_color="#101010", bg_color="#FFFFFF",
                                                  fg_color="#FFFFFF", font=SMALLFONT, height=48, button_color="#FFFFFF",
                                                  button_hover_color="#FFFFFF", dropdown_font=SMALLFONT,
                                                  dropdown_hover_color="#F0F0F0", dropdown_fg_color="#FFFFFF",
                                                  dropdown_text_color="#101010")
            self.svmKernelBox.grid(row=0, column=4, padx=4, pady=0, sticky="w")

            GammaLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Gamma:", text_color="#FFFFFF", font=SMALLFONT)
            GammaLabel.grid(row=0, column=5, padx=(0, 4), sticky="w")

            self.svmGammaEntry = ctk.CTkEntry(self.ModelConfigFrame, width=100, height=24)
            self.svmGammaEntry.grid(row=0, column=6, padx=4, sticky="w")
            
            RandomStateLabel = ctk.CTkLabel(self.ModelConfigFrame, text="Random state:", text_color="#FFFFFF", font=SMALLFONT)
            RandomStateLabel.grid(row=0, column=7, padx=(0, 4), sticky="w")

            self.svmRandomStateEntry = ctk.CTkEntry(self.ModelConfigFrame, width=100, height=24)
            self.svmRandomStateEntry.grid(row=0, column=8, padx=4, sticky="w")

            self.MetricsFrame.columnconfigure(2, weight=1)
        
        self.TrainButton.configure(state="normal")
        self.TestButton.configure(state="disabled")
        self.SaveModelButton.configure(state="disabled")
        self.showMetricsPlotsBtn.configure(state="disabled")

    def train_mlModel(self):
        global DATA

        if self.ModelTypeCombobox.get() == 'Model type':
            tk.messagebox.showerror("Information", "Please choose a model type")
            return
        
        for widget in self.NumericMetricsFrame.winfo_children():
            widget.destroy()

        for widget in self.ConfusionMatrixFrame.winfo_children():
            widget.destroy()

        for widget in self.ROCCurveFrame.winfo_children():
            widget.destroy()
        
        if DATA.mlModelType == 'Linear Regression':
            DATA.mlModel = LinearRegression()

        elif DATA.mlModelType == 'Naive Bayes':
            nbDistribution = self.nbDistributionBox.get()

            if nbDistribution == '' or nbDistribution == None or nbDistribution == 'Gaussian':
                DATA.mlModel = GaussianNB()
            elif nbDistribution == 'Multinomial':
                DATA.mlModel = MultinomialNB()
            elif nbDistribution == 'Bernoulli':
                DATA.mlModel = BernoulliNB()

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
                kmAlgorithm = 'lloyd'
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
        
        if DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None or DATA.X is None or DATA.y is None:
            if DATA.mlModelType == 'K-means':
                DATA.mlModel.fit(concat([DATA.X, DATA.y], axis=1))
            else:
                DATA.mlModel.fit(DATA.X, DATA.y)
        else:
            if DATA.mlModelType == 'K-means':
                DATA.mlModel.fit(concat([DATA.X_train, DATA.y_train], axis=1))
            else:
                DATA.mlModel.fit(DATA.X_train, DATA.y_train)

        self.TestButton.configure(state="normal")
        self.SaveModelButton.configure(state="normal")

    def test_mlModel(self):
        global DATA
        
        try:
            if DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None or DATA.X is None or DATA.y is None:
                if DATA.mlModelType == 'K-means':
                    self.prediction = DATA.mlModel.predict(concat([DATA.X, DATA.y], axis=1))
                else:
                    self.prediction = DATA.mlModel.predict(DATA.X)
            else:
                if DATA.mlModelType == 'K-means':
                    self.prediction = DATA.mlModel.predict(concat([DATA.X_test, DATA.y_test], axis=1))
                else:
                    self.prediction = DATA.mlModel.predict(DATA.X_test)
        except Exception as e:
            tk.messagebox.showerror("Information", f"An error occurred while trying to predict data: {e}")
            return

        if DATA.mlModelType == 'Linear Regression':
            self.MaxErrorLabel = ctk.CTkLabel(self.NumericMetricsFrame,
                                              text=f"Max error: {round(metrics.max_error(DATA.y if (DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None or DATA.X is None or DATA.y is None) else DATA.y_test, self.prediction), 4)}",
                                              text_color="#FFFFFF", font=MEDIUMFONT)
            self.MaxErrorLabel.grid(row=2, column=0, padx=0, pady=8, sticky="w")

            self.MAELabel = ctk.CTkLabel(self.NumericMetricsFrame,
                                         text=f"Mean absolute error: {round(metrics.mean_absolute_error(DATA.y if (DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None or DATA.X is None or DATA.y is None) else DATA.y_test, self.prediction), 4)}",
                                         text_color="#FFFFFF", font=MEDIUMFONT)
            self.MAELabel.grid(row=3, column=0, padx=0, pady=8, sticky="w")

            self.MSELabel = ctk.CTkLabel(self.NumericMetricsFrame,
                                         text=f"Mean squared error: {round(metrics.mean_squared_error(DATA.y if (DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None or DATA.X is None or DATA.y is None) else DATA.y_test, self.prediction), 4)}",
                                         text_color="#FFFFFF", font=MEDIUMFONT)
            self.MSELabel.grid(row=4, column=0, padx=0, pady=8, sticky="w")

            self.R2Label = ctk.CTkLabel(self.NumericMetricsFrame,
                                        text=f"R2 score: {round(metrics.r2_score(DATA.y if (DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None or DATA.X is None or DATA.y is None) else DATA.y_test, self.prediction), 4)}",
                                        text_color="#FFFFFF", font=MEDIUMFONT)
            self.R2Label.grid(row=5, column=0, padx=0, pady=8, sticky="w")

            self.showMetricsPlotsBtn.configure(state="disabled")

        elif DATA.mlModelType == 'K-means':
            self.SaveModelButton.configure(state="normal")
            self.showMetricsPlotsBtn.configure(state="normal")

        else:
            self.cm = metrics.confusion_matrix(DATA.y if (DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None or DATA.X is None or DATA.y is None) else DATA.y_test, self.prediction)
            BER = 1 - (1/2 * ((self.cm[0][0] / (self.cm[0][0] + self.cm[1][0])) + (self.cm[1][1] / (self.cm[1][1] + self.cm[0][1]))))
    
            self.BERLabel = ctk.CTkLabel(self.NumericMetricsFrame, text=f"Balanced Error Rate: {round(BER, 4)}", text_color="#FFFFFF", font=MEDIUMFONT)
            self.BERLabel.grid(row=3, column=0, padx=0, pady=8, sticky = "w")

            self.BERLabel = ctk.CTkLabel(self.NumericMetricsFrame, text=f"Balanced Error Rate: {round(BER, 4)}",
                                         text_color="#FFFFFF", font=MEDIUMFONT)
            self.BERLabel.grid(row=3, column=0, padx=0, pady=8, sticky="w")

            self.AccuracyLabel = ctk.CTkLabel(self.NumericMetricsFrame,
                                              text=f"Accuracy: {round(metrics.accuracy_score(DATA.y if (DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None or DATA.X is None or DATA.y is None) else DATA.y_test, self.prediction), 4)}",
                                              text_color="#FFFFFF", font=MEDIUMFONT)
            self.AccuracyLabel.grid(row=4, column=0, padx=0, pady=8, sticky="w")

            self.PrecisionLabel = ctk.CTkLabel(self.NumericMetricsFrame,
                                               text=f"Precision: {round(metrics.precision_score(DATA.y if (DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None or DATA.X is None or DATA.y is None) else DATA.y_test, self.prediction), 4)}",
                                               text_color="#FFFFFF", font=MEDIUMFONT)
            self.PrecisionLabel.grid(row=5, column=0, padx=0, pady=8, sticky="w")

            self.RecallLabel = ctk.CTkLabel(self.NumericMetricsFrame,
                                            text=f"Recall: {round(metrics.recall_score(DATA.y if (DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None or DATA.X is None or DATA.y is None) else DATA.y_test, self.prediction), 4)}",
                                            text_color="#FFFFFF", font=MEDIUMFONT)
            self.RecallLabel.grid(row=6, column=0, padx=0, pady=8, sticky="w")

            self.F1ScoreLabel = ctk.CTkLabel(self.NumericMetricsFrame,
                                             text=f"F1 score: {round(metrics.f1_score(DATA.y if (DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None or DATA.X is None or DATA.y is None) else DATA.y_test, self.prediction), 4)}",
                                             text_color="#FFFFFF", font=MEDIUMFONT)
            self.F1ScoreLabel.grid(row=7, column=0, padx=0, pady=8, sticky="w")

            self.AUCScoreLabel = ctk.CTkLabel(self.NumericMetricsFrame,
                                              text=f"AUC score: {round(metrics.roc_auc_score(DATA.y if (DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None or DATA.X is None or DATA.y is None) else DATA.y_test, self.prediction), 4)}",
                                              text_color="#FFFFFF", font=MEDIUMFONT)
            self.AUCScoreLabel.grid(row=8, column=0, padx=0, pady=8, sticky="w")

            self.SaveModelButton.configure(state="normal")
            self.showMetricsPlotsBtn.configure(state="normal")

    def showMetricsPlots(self):
        global DATA
        global app
        
        for widget in self.ConfusionMatrixFrame.winfo_children():
            widget.destroy()

        for widget in self.ROCCurveFrame.winfo_children():
            widget.destroy()

        if DATA.mlModelType == 'K-means':
            self.ColumnXOptionmenuVar = ctk.StringVar(value="Column X")
            self.ColumnXCombobox = ctk.CTkOptionMenu(master=self.NumericMetricsFrame,
                                                    values=get_dataframe_columns(DATA.file_data),
                                                    variable=self.ColumnXOptionmenuVar,
                                                    width=150, corner_radius=0, text_color="#101010",
                                                    bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=32,
                                                    button_color="#FFFFFF", button_hover_color="#FFFFFF",
                                                    dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0",
                                                    dropdown_fg_color="#FFFFFF", dropdown_text_color="#101010")
            self.ColumnXCombobox.grid(row=0, column=0, padx=0, pady=(0, 4), ipadx=8, ipady=8, sticky="ew")

            self.ColumnYOptionmenuVar = ctk.StringVar(value="Column Y")
            self.ColumnYCombobox = ctk.CTkOptionMenu(master=self.NumericMetricsFrame,
                                                    values=get_dataframe_columns(DATA.file_data),
                                                    variable=self.ColumnYOptionmenuVar,
                                                    width=150, corner_radius=0, text_color="#101010",
                                                    bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT, height=32,
                                                    button_color="#FFFFFF", button_hover_color="#FFFFFF",
                                                    dropdown_font=SMALLFONT, dropdown_hover_color="#F0F0F0",
                                                    dropdown_fg_color="#FFFFFF", dropdown_text_color="#101010")
            self.ColumnYCombobox.grid(row=1, column=0, padx=0, pady=4, ipadx=8, ipady=8, sticky="ew")

            PlotButton = ctk.CTkButton(self.NumericMetricsFrame, text="Plot", command=lambda: self.showKmeansPlots(),
                                   corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF",
                                   font=SMALLFONT, hover_color="#F0F0F0", height=32)
            PlotButton.grid(row=2, column=0, padx=0, pady=4, ipadx=8, ipady=8, sticky="ew")

        elif DATA.mlModelType != 'Linear Regression':
            disp = metrics.ConfusionMatrixDisplay.from_predictions(y_true=DATA.y if (DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None or DATA.X is None or DATA.y is None) else DATA.y_test, y_pred=self.prediction, display_labels=["False", "True"], cmap=plt.cm.Blues)
            fpr, tpr, thresh = metrics.roc_curve(DATA.y if (DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None or DATA.X is None or DATA.y is None) else DATA.y_test, self.prediction, pos_label=1)
            roc_display = metrics.RocCurveDisplay(fpr=fpr, tpr=tpr)

            self.figure1 = Figure()

            # create FigureCanvasTkAgg object
            self.figure_canvas1 = FigureCanvasTkAgg(self.figure1, self.ConfusionMatrixFrame)

            # create axes
            self.axe1 = self.figure1.add_subplot()

            disp.plot(ax=self.axe1)
            self.axe1.legend([""], fontsize="x-large")
            self.axe1.set_xlabel("")
            self.axe1.set_title("Confusion matrix")

            self.figure2 = Figure()

            # create FigureCanvasTkAgg object
            self.figure_canvas2 = FigureCanvasTkAgg(self.figure2, self.ROCCurveFrame)

            # create axes
            self.axe2 = self.figure2.add_subplot()

            roc_display.plot(ax=self.axe2)
            self.axe2.legend([""], fontsize="x-large")
            self.axe2.set_xlabel("")
            self.axe2.set_title("ROC curve")

            self.figure_canvas1.draw()
            self.figure_canvas2.draw()
            self.figure_canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.figure_canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def showKmeansPlots(self):
        for widget in self.ConfusionMatrixFrame.winfo_children():
            widget.destroy()

        for widget in self.ROCCurveFrame.winfo_children():
            widget.destroy()

        if DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None or DATA.X is None or DATA.y is None:
            new_points = concat([DATA.X, DATA.y], axis=1).to_numpy()
        else:
            new_points = concat([DATA.X_test, DATA.y_test], axis=1).to_numpy()


        xc = self.ColumnXCombobox.get()
        yc = self.ColumnYCombobox.get()

        if xc == 'Column X' or yc == 'Column Y':
            tk.messagebox.showerror("Information", "Please choose columns")
            return
        xi = get_dataframe_columns(DATA.file_data).index(xc)
        yi = get_dataframe_columns(DATA.file_data).index(yc)

        xs = new_points[:, xi]
        ys = new_points[:, yi]
                        
        centroids = DATA.mlModel.cluster_centers_

        centroids_x = centroids[:, xi]
        centroids_y = centroids[:, yi]

        self.figure1 = Figure()

        self.figure_canvas1 = FigureCanvasTkAgg(self.figure1, self.ConfusionMatrixFrame)

        self.axe1 = self.figure1.add_subplot()
        self.axe1.scatter(xs, ys, c=self.prediction, alpha=0.5, s=10)
        self.axe1.scatter(centroids_x, centroids_y, marker='D', s=10)
        self.axe1.legend([""], fontsize="x-large")
        self.axe1.set_xlabel("")
        self.axe1.set_title("Clusters")

        self.figure_canvas1.draw()
        self.figure_canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def importModelHandler(self):
        file_path, file_extension = UploadAction(type="model")

        if file_path == None or file_path == '':
            return
        
        if file_extension != '.sav':
            tk.messagebox.showerror("Information", "Please select a valid file")
            return
        
        global DATA

        DATA.mlModel = load(file_path)

        self.TrainButton.configure(state="normal")
        self.TestButton.configure(state="normal")
        self.SaveModelButton.configure(state="normal")
        self.showMetricsPlotsBtn.configure(state="disabled")

        self.ModelTypeCombobox.set('Model type')

        for widget in self.ModelConfigFrame.winfo_children():
            widget.destroy()

        for widget in self.NumericMetricsFrame.winfo_children():
            widget.destroy()

        for widget in self.ConfusionMatrixFrame.winfo_children():
            widget.destroy()
        
        for widget in self.ROCCurveFrame.winfo_children():
            widget.destroy()

    def openSaveModelWindow(self):
        try:
            if DATA.X_train is None or DATA.y_train is None or DATA.X_test is None or DATA.y_test is None:
                DATA.mlModel.predict(DATA.X)
            else:
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
        self.geometry("300x218")
        self.iconbitmap('./assets/icons/machine-learning.ico')
        self.configure(bg_color="#101010", fg_color="#101010", width=200)
        self.title("Save model")

        self.columnconfigure(0, weight=1)

        Title = ctk.CTkLabel(self, text="Save model", text_color="#FFFFFF", font=LARGEFONT)
        Title.grid(row=0, column=0, padx=8, pady=8, sticky="w")

        EntryFrame = ctk.CTkFrame(self, fg_color="#191919")
        EntryFrame.grid(row=1, column=0, ipadx=0, ipady=0, columnspan=3, sticky="ew")

        EntryFrame.columnconfigure(1, weight=1)

        Label = ctk.CTkLabel(EntryFrame, text="File name:", text_color="#FFFFFF", font=SMALLFONT)
        Label.grid(row=0, column=0, padx=8, pady=8, sticky = "w")

        self.FileName_entry = ctk.CTkEntry(EntryFrame, width=100, height=24)
        self.FileName_entry.grid(row=0, column=1, padx=8, pady=8, sticky="ew")

        ChooseDirButton = ctk.CTkButton(self, text="Choose directory", command=lambda: self.SelectSaveDirectory(),
                                        corner_radius=0, text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF",
                                        font=SMALLFONT, hover_color="#F0F0F0", height=48, width=56)
        ChooseDirButton.grid(row=2, column=0, padx=8, pady=(8, 4), sticky="ew")

        SaveFileButton = ctk.CTkButton(self, text="Save file", command=lambda: self.SaveFile(), corner_radius=0,
                                       text_color="#101010", bg_color="#FFFFFF", fg_color="#FFFFFF", font=SMALLFONT,
                                       hover_color="#F0F0F0", height=48, width=56)
        SaveFileButton.grid(row=3, column=0, padx=8, pady=4, sticky="ew")

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
            
            dump(DATA.mlModel, self.SaveDirectory + "/" + self.FileName_entry.get() + ".sav")

            self.destroy()
            self.update()

        else:
            tk.messagebox.showerror("Information", "Please select a directory")
            return
        
# DRIVER CODE
app = App()
app.protocol("WM_DELETE_WINDOW", Exit)
app.mainloop()
