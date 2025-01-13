import os
from typing import List

import pandas as pd


def load_user_list(config_root: str, course_name: str, semester: str) -> List[str]:
    users = []
    try:
        user_list_file = os.path.join(config_root, f"{course_name}-{semester}.csv")
        print(user_list_file)
        userlist = pd.read_csv(user_list_file)
        if "Username" in userlist.columns:
            users = list(userlist.Username)
    except FileNotFoundError:
        pass
    return users
