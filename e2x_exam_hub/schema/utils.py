from typing import List

import pandas as pd


def load_user_list(user_list_file: str) -> List[str]:
    """
    Load a list of usernames from a CSV file.

    Args:
        user_list_file (str): The path to the CSV file containing the user list.

    Returns:
        List[str]: A list of usernames extracted from the CSV file. If the file is not found,
        returns an empty list.
    """
    users = []
    try:
        userlist = pd.read_csv(user_list_file)
        if "Username" in userlist.columns:
            users = list(userlist.Username)
    except FileNotFoundError:
        pass
    return users
