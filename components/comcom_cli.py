import os

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.tree import Tree

from datetime import datetime
from enum import Enum

from services import DataService, DirectoryService

from .exceptions import ParserArgumentException


# Log Level Enum
class LogLevel(Enum):
        DEBUG = 10
        INFO = 20
        WARNING = 30
        ERROR = 40
        CRITICAL = 50

# ComComCLI Class
class ComComCLI():

    # Log level
    @classmethod
    def GetLogLevel(cls) -> LogLevel:
        cls.__singleton()
        return cls.__instance.__log_level

    @classmethod
    def SetLogLevel(cls, value: LogLevel):
        cls.__singleton()
        cls.__instance.__log_level = value

    # Constructor
    def __init__(self) -> None:
        self.__console = Console()
        self.__log_level: LogLevel = LogLevel["INFO"]

    # Singleton
    @classmethod
    def __singleton(cls):
        if not cls.__instance: ComComCLI()
    
    __instance = None
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(ComComCLI, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    # Utilities
    @classmethod
    def cli(cls):
        cls.__singleton()
        return cls.__instance.__console

    # Printing Methods   
    @classmethod
    def printHeadline(cls, head: str, text: str):
        cls.__singleton()
        headline = Panel(
            Text(text, justify="center", style="bold #000000 on #FC6D26"),
            title=head,
            title_align="center",
            border_style="bold #E24329"
        )
        cls.cli().print(headline)

    @classmethod
    def printSeparator(cls):
        cls.__singleton()
        terminal_width = cls.cli().width
        line = "-" * terminal_width
        cls.cli().print(line)

    @classmethod
    def printPathTree(cls, path):
        cls.__singleton()
        tree = cls.__instance.__create_file_tree(path)
        cls.cli().print(tree)

    def __create_file_tree(self, path: str) -> Tree:
        basename = os.path.basename(path)
        tree = Tree(f"[bold #CCCCCC]{basename}", guide_style="#555555")
        self.__add_files(tree, path)
        return tree

    def __add_files(self, tree: Tree, path: str):
        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=True):
                if not os.listdir(entry.path) or entry.name == ".git":
                    continue
                branch = tree.add(f"[bold #CCCCCC]{entry.name}")
                self.__add_files(branch, entry.path)
            else:
                if DataService.IsNewFile(entry.name):
                    tree.add(f"[bold #CCCCCC]{entry.name}")
    
    # Exit Visualization
    @classmethod
    def printExitError(cls, message:str, e: Exception):
        cls.__singleton()
        text = f"{message}\n{str(e)}"
        headline = Panel(
            Text(text, justify="center", style=""),
            title="Error",
            title_align="center",
            border_style="bold #660000"
        )
        cls.cli().print_exception()
        cls.cli().print(headline)

    @classmethod
    def printExitParserError(cls, pae: ParserArgumentException):
        cls.__singleton()
        message = Text(str(pae), justify="center", style="#888888")
        if(pae.Solution): message += Text("\n") + Text.from_markup(f"[white][underline]Solution[/underline][/]: {pae.Solution}")
        headline = Panel(
            message,
            title="Parsing Error",
            title_align="center",
            border_style="bold #555500"
        )
        cls.cli().print(headline)

    @classmethod
    def printExitSuccess(cls, message: str):
        cls.__singleton()
        print()
        title=Text(message, justify="center", style="")
        tree = cls.__instance.__create_file_tree(DirectoryService.App())

        layout = Table(show_header=False, box=None)
        half = cls.cli().width // 2
        layout.add_column("Message", width=half, justify="left")
        layout.add_column("Tree", width=half, justify="left")        
        layout.add_row("Message: ", "Files: ")
        layout.add_row("", "")
        layout.add_row(title, tree)
        
        headline = Panel(
            layout,
            title="Success",
            title_align="left",
            border_style="bold bright_green"
        )
        cls.cli().print(headline)

    # Logging
    def __set_log_layout_header(self, layout: Table, style=""):
        layout.add_column("Time", width=40, justify="left", style=style)
        layout.add_column("Level", width=25, justify="left", style=style)
        layout.add_column("Message", width=50, justify="left", style=style)
        layout.add_column("Details", width=100, justify="left", style=style)

    def __create_log_layout(self, style="") -> Table:
        layout = Table(show_header=False, box=None)
        self.__set_log_layout_header(layout, style=style)
        return layout
    
    @classmethod
    def logSection(cls, title: str):
        cls.__singleton()
        print("\n")
        sectionTitle = Text(title, style="bold white", justify="center")
        sectionTitle.stylize("bold", 25) 

        layout = Table(show_header=True, box=None, header_style="bold", caption_justify="left")
        layout.add_column(header=sectionTitle, width=40+25+50+100, justify="center")

        cls.cli().print(layout)

    @classmethod
    def logHeader(cls):
        cls.__singleton()
        print()
        layout = Table(show_header=True, box=None, header_style="bold", caption_justify="left")
        cls.__instance.__set_log_layout_header(layout, style="bold on green")
        cls.cli().print(layout)

    @classmethod
    def log(cls, level: LogLevel, message: str, details):
        cls.__singleton()

        # Log Level
        if cls.__instance.__log_level.value > level.value:
            return

        # Process data
        if isinstance(details, Exception):
            detail_str = f"Exception: {str(details)}"
        elif isinstance(details, list) and all(isinstance(item, str) for item in details):
            detail_str = " ".join([str(detail) for detail in details])
        else:
            detail_str = details

        # Layout
        match level.name:
            case "CRITICAL":
                layout = cls.__instance.__create_log_layout(style="bold on #660000")
            case "ERROR":
                layout = cls.__instance.__create_log_layout(style="#660000")
            case "WARNING":
                layout = cls.__instance.__create_log_layout(style="#CCCC00")
            case "DEBUG":
                layout = cls.__instance.__create_log_layout(style="#555555")
            case _:
                layout = cls.__instance.__create_log_layout(style="#CCCCCC")

        # Add data and create log
        timestamp = datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
        layout.add_row(timestamp, level.name, message, detail_str)
        cls.cli().print(layout)