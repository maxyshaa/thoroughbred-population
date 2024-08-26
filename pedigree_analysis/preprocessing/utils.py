"""This module contains universal functions"""

import pandas as pd
import os
from typing import Union

def save_file(data: Union[pd.DataFrame, set], path: str, filename: str) -> None:
    """
    Save a DataFrame or a set to a CSV file.
    Args:
        data: the data to save, either a pandas DataFrame or a python set
        path: the directory path where the file will be saved
        filename: the name of the output CSV file
    Returns:
        None
    Raises:
        FileNotFoundError: if the specified directory does not exist.
        ValueError: if the provided filename is not valid or the data type is not supported.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"The directory {path} does not exist.")
    
    if not filename.endswith(".csv"):
        raise ValueError("The filename must end with .csv")
    
    file_path = os.path.join(path, filename)
    
    if isinstance(data, pd.DataFrame):
        data.to_csv(path_or_buf=file_path, sep=",", index=False)
    elif isinstance(data, set):
        df = pd.DataFrame(data)
        df.to_csv(path_or_buf=file_path, sep=",", index=False, header=False)
    print(f"File saved to {file_path}")