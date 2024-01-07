from pandas import DataFrame, concat
from numpy import abs, percentile
from scipy import stats
from sklearn.feature_selection import VarianceThreshold, SelectKBest, f_classif
from enums import enums

def get_dataframe_columns(df: list | DataFrame):    
    return df.columns.values.tolist()

def get_dataframe_features(df: list | DataFrame):    
    return df.columns.values.tolist()

def get_constant_columns(df: list | DataFrame):
    return [col for col in df.columns if len(df[col].unique()) <= 1]

def get_non_constant_columns(df: list | DataFrame):
    return [col for col in df.columns if len(df[col].unique()) > 1]

def drop_contant_columns(df: list | DataFrame):
    df.loc[:, (df != df.iloc[0]).any()]

def drop_duplicate_rows(df: list | DataFrame):
    df.drop_duplicates(inplace=True)

def handle_missing_values(df: list | DataFrame, value: int | float | str = None, method: enums.FillMethod = enums.FillMethod.DROP):
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

def remove_outliers(df: list | DataFrame, method: enums.OutlierMethod = enums.OutlierMethod.ZSCORE):   
    if method == enums.OutlierMethod.ZSCORE:
        for col in df.columns:
            df[abs(stats.zscore(df[col])) < 3]
    elif method == enums.OutlierMethod.IQR:
        for col in df.columns[:-2]:
            if df.shape[0] != 0:
                q1, q3 = percentile(df[col], [25, 75], method='midpoint')
                iqr = q3 - q1
                upper_bound = q3 + (1.5 * iqr)
                lower_bound = q1 - (1.5 * iqr)
                df = df[((df > lower_bound) & (df < upper_bound)).any(axis=1)]


def feature_selection_kBestFeatures(df: list | DataFrame, k: int):
    X = df[:, :-1]
    y = df[:, -1]
    skb = SelectKBest(score_func=f_classif, k=k)

    return concat([DataFrame(skb.fit_transform(X, y)), DataFrame(y)], axis=1)

def feature_selection_varianceThreshold(df, threshold):
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    vt = VarianceThreshold(threshold=threshold)

    selected_data = vt.fit_transform(X)

    selected_data = concat([DataFrame(selected_data), DataFrame(y)], axis=1)

    return selected_data