import pandas as pd
import numpy as np
from sklearn.feature_selection import VarianceThreshold, SelectKBest, f_classif
import tkinter as tk
from enums import enums

def get_non_constant_columns(df: list | pd.DataFrame):
    return [col for col in df.columns if len(df[col].unique()) > 1]

def drop_contant_columns(df: list | pd.DataFrame):
    df.loc[:, (df != df.iloc[0]).any()]

def drop_duplicate_rows(df: list | pd.DataFrame):
    df.drop_duplicates(inplace=True)

def handle_missing_values(df: list | pd.DataFrame, value: int | float | str = None, method: enums.FillMethod = enums.FillMethod.DROP):
    if value is not None:
        df.fillna(value, inplace=True)
    else:
        if method == enums.FillMethod.DROP:
            df.dropna(inplace=True)
        elif method == enums.FillMethod.MEAN:
            df.fillna(df.mean(numeric_only=True), inplace=True)
        elif method == enums.FillMethod.MEDIAN:
            df.fillna(df.median(numeric_only=True), inplace=True)
        elif method == enums.FillMethod.MODE:
            df.fillna(df.mode(numeric_only=True), inplace=True)
        elif method == enums.FillMethod.ZERO:
            df.fillna(0, inplace=True)
        

def feature_selection_kBestFeatures(df: list | pd.DataFrame, k: int):
    X = df[:, :-1]
    y = df[:, -1]
    skb = SelectKBest(score_func=f_classif, k=k)

    return pd.concat([pd.DataFrame(skb.fit_transform(X, y)), pd.DataFrame(y)], axis=1)

def feature_selection_varianceThreshold(df: list | pd.DataFrame, threshold: float):
    X = df[:, :-1]
    y = df[:, -1]
    vt = VarianceThreshold(threshold=threshold)

    return pd.DataFrame(vt.fit_transform(X, y))