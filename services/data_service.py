import os
from datetime import datetime
from typing import List

class DataService:

    # Class roperties
    @classmethod
    def Timestamp(cls) -> str:
        cls.__singleton()
        return cls.__instance.__timestamp
    
    @classmethod
    def AddNewFile(cls, value) -> None:
        cls.__singleton()
        trimmed = os.path.basename(value)
        cls.__instance.__new_files.append(trimmed)

    @classmethod
    def GetNewFiles(cls) -> List[str]:
        cls.__singleton()
        return cls.__instance.__new_files

    @classmethod
    def IsNewFile(cls, value) -> bool:
        cls.__singleton()
        isnew = value in cls.__instance.__new_files
        return isnew

    # Constructor
    def __init__(self) -> None:
        self.__timestamp = datetime.now().strftime("%d.%m.%Y - %H:%M")
        self.__new_files: List[str] = []

    # Singleton
    @classmethod
    def __singleton(cls):
        if not cls.__instance: DataService()
    
    __instance = None
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(DataService, cls).__new__(cls, *args, **kwargs)
        return cls.__instance