import pandas as pd
import numpy as np
from sklearn.feature_selection import VarianceThreshold, SelectKBest, f_classif
import tkinter as tk


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