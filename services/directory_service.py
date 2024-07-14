import os

class DirectoryService:

    # Class Properties
    @classmethod
    def Root(cls) -> str:
        cls.__singleton()
        return cls.__instance.__rootDir

    @classmethod
    def App(cls) -> str:
        cls.__singleton()
        return cls.__instance.__appDir

    @classmethod
    def Environments(cls) -> str:
        cls.__singleton()
        return cls.__instance.__envDir

    @classmethod
    def Resources(cls) -> str:
        cls.__singleton()
        return cls.__instance.__resDir

    @classmethod
    def Templates(cls) -> str:
        cls.__singleton()
        return cls.__instance.__tempDir
    
    @classmethod
    def Build(cls) -> str:
        cls.__singleton()
        return cls.__instance.__buildDir

    @classmethod
    def Container(cls) -> str:
        cls.__singleton()
        return "/usr/src/app/"

    @classmethod
    def UseGitLab(cls) -> None:
        cls.__instance.__appDir = os.getcwd()
        cls.__instance.__ensure_directory(cls.__instance.__appDir)
        cls.__instance.__buildDir = os.path.join(cls.__instance.__appDir, "comcom")
        cls.__instance.__ensure_directory(cls.__instance.__buildDir)
        #print(f"DEBUGGING:\nApp=[{cls.App()}]\nBuild=[{cls.Build()}]")

    # Constructor
    def __init__(self) -> None:
        self.__rootDir = self.__get_root()
        self.__appDir = os.path.join(self.__rootDir, "app")
        self.__ensure_directory(self.__appDir)
        self.__buildDir = os.path.join(self.__appDir, "comcom")
        self.__ensure_directory(self.__buildDir)
        self.__envDir = os.path.join(self.__rootDir, "environments")
        self.__resDir = os.path.join(self.__rootDir, "resources")
        self.__tempDir = os.path.join(self.__rootDir, "templates")

    def __ensure_directory(self, dir):
        os.makedirs(dir, exist_ok=True)

    def __get_root(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        while not os.path.isfile(os.path.join(current_dir, "README.md")):
            current_dir = os.path.dirname(current_dir)
            if current_dir == os.path.dirname(current_dir):
                raise FileNotFoundError("Could not find the project root directory.")
        return current_dir
    
    # Singleton
    @classmethod
    def __singleton(cls):
        if not cls.__instance: DirectoryService()
    __instance = None
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(DirectoryService, cls).__new__(cls, *args, **kwargs)
        return cls.__instance
