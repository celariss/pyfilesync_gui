from enum import Enum

from syncconfig import *

class CmpStatus(Enum):
    LEFT_ONLY = 1
    RIGHT_ONLY = 2
    DIFFERENT = 3
    
class ResultItem:
    def __init__(self, status:CmpStatus, left_dir, left_file, right_dir, right_file, pair_index:int):
        """Represents a single result item in the comparison results.
        Args:
            status (CmpStatus): The comparison status (LEFT_ONLY, RIGHT_ONLY, DIFFERENT).
            left_dir (str): The directory base path on the left side.
            left_file (str): The file path on the left side, relative to the left base directory.
            right_dir (str): The directory base path on the right side.
            right_file (str): The file path on the right side, relative to the right base directory.
            pair_index (int): The index of the pair in the configuration.
        """
        self.left_dir = left_dir
        self.left_file = left_file
        self.include = True
        self.status:CmpStatus = status
        self.right_dir = right_dir
        self.right_file = right_file
        self.pair_index = pair_index

class UIInterface:
    def show_error(self, message:str):
        pass
    
    def refresh(self):
        pass

    def set_config_data(self, config:SyncConfig):
        pass

    def clear_results(self):
        pass

    def refresh_results(self):
        pass

    def append_result(self, item: ResultItem):
        pass