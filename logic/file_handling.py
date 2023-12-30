from customtkinter import filedialog
import os
import pandas as pd
import tkinter as tk
import customtkinter as ctk

class file_handling:
    def __init__(self, file_path, file_extension):
        self.file_path: str = file_path
        self.file_extension: str = file_extension
        self.file_data: pd.DataFrame = None
        self.X: pd.DataFrame = None
        self.y: pd.DataFrame = None
        self.X_train: pd.DataFrame = None
        self.X_test: pd.DataFrame = None
        self.y_train: pd.DataFrame = None
        self.y_test: pd.DataFrame = None
        # self.file_data_columns = None
        # self.file_data_rows = None
        # self.file_data_shape = None
        # self.file_data_size = None
        # self.file_data_type = None
        # self.file_data_head = None
        # self.file_data_tail = None
        # self.file_data_info = None
        # self.file_data_describe = None
        # self.file_data_duplicated = None
        # self.file_data_duplicated_count = None
        # self.file_data_duplicated_index = None
        # self.file_data_duplicated_index_count = None
        # self.file_data_duplicated_index_drop = None

    def __str__(self) -> str:
        return f"File path: {self.file_path}\nFile extension: {self.file_extension}\nFile data: {self.file_data}\nFile columns: {self.file_data.columns.values.tolist()}"
        
    """     def UploadAction(self):
            self.file_path = filedialog.askopenfilename()
            print('Selected:', self.file_path)
            if not self.file_path:
                return
            _, self.file_extension = os.path.splitext(self.file_path) """
        
    def file_data_read(self):
        try:
            if self.file_extension == '.csv':
                self.file_data = pd.read_csv(self.file_path)
            elif self.file_extension == '.xlsx':
                self.file_data = pd.read_excel(self.file_path)
            elif self.file_extension == '.json':
                self.file_data = pd.read_json(self.file_path)
            elif self.file_extension == '.txt':
                self.file_data = pd.read_csv(self.file_path, sep=' ', header=None)
            return None

        except ValueError:
            ctk.messagebox.showerror("Information", "The file you have chosen is invalid")
            return None
        except FileNotFoundError:
            ctk.messagebox.showerror("Information", f"No such file as {self.file_path}")
            return None
        