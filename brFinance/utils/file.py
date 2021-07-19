import os
from dataclasses import dataclass


@dataclass
class File:
    def __init__(self, directory: str) -> None:
        self.directory = directory
        
    def check_exist(self) -> bool:
        if os.path.isfile(self):
            return True
        else:
            return False
    
    def create_folder(self) -> None:
        try:
            os.makedirs(self)
        except FileExistsError:
            # directory already exists
            pass