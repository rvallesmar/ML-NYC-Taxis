import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler

def preprocess_data(
    train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Pre processes data for modeling. Receives a previously cleaned dataframe
    for each of the train, validation and testing sets to be used
    and returns numpy ndarrays of processed dataframe with feature engineering
    already performed.

    Arguments:
        train_df : pd.DataFrame
        val_df : pd.DataFrame
        test_df : pd.DataFrame
    Returns:
        train : np.ndarrary
        val : np.ndarrary
        test : np.ndarrary
    """

    # Printing the original shape of the input data
    print("Input train data shape: ", train_df.shape)
    print("Input val data shape: ", val_df.shape)
    print("Input test data shape: ", test_df.shape, "\n")

    # making a copy of the dataframe to do changes
    working_train_df = train_df.copy()
    working_val_df = val_df.copy()
    working_test_df = test_df.copy()

    # 1
    # we only have one categorical feature in our cleaned data set which is time_of_day
    # and it has 3 categories, so we can use OneHotEncoder for this task

    one_hot_enc = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    # first fit and transform training data
    train_data = one_hot_enc.fit_transform(working_train_df[['time_of_day']])
    #transform the others
    val_data = one_hot_enc.transform(working_val_df[['time_of_day']])
    test_data = one_hot_enc.transform(working_test_df[['time_of_day']])



    # 2
    # since we do not expect to have any null values in our dataset (its supposed to have been
    # previously cleaned), then we can just proceed to apply MinMax scaling to all of the columns
    scaler = MinMaxScaler()

    train_scaled = scaler.fit_transform(working_train_df.drop(columns=['time_of_day']))
    val_scaled = scaler.transform(working_val_df.drop(columns=['time_of_day']))
    test_scaled = scaler.transform(working_test_df.drop(columns=['time_of_day']))

    train = np.concatenate((train_scaled,train_data), axis=1)
    val = np.concatenate((val_scaled,val_data), axis=1)
    test = np.concatenate((test_scaled,test_data), axis=1)

    print("Output train data shape: ", train.shape)
    print("Output val data shape: ", val.shape)
    print("Output test data shape: ", test.shape)

    return train, val, test
