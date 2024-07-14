import shutil
import os
from services import DirectoryService, DataService

class Template:

    # Default values
    documentProperties = {
        "Title": "ReleaseNotes",
        "Author": "CommitCompiler",
        "Keywords": "",
        "Subject": "Release Notes created with CommitCompiler"
    }
    exampleOptionals = {
        "title": "Commit Compiler Example",
        "subtitle": "Create release documentation the easy way.",
        "date": DataService.Timestamp(),
        "github-url": "https://github.com/FaSeEngineering/CommitCompiler",
        "github-alias": "Repository"
    }
    exampleMD = "example.md"
    exampleLayout = "layout.html"
    exampleVersion = "1.5.0"
    exampleBuild = "a3f5e6b2"

    defaultLogo = "logo.png"

    # Temporary files dictionary
    temp_files = []

    # Methods
    @classmethod 
    def __copy_file(cls, source_file: str, destination_file: str):
        if os.path.isfile(source_file):
            shutil.copy2(source_file, destination_file)

    @classmethod
    def useExample(cls):

        # Example markdown file
        source_file = os.path.join(DirectoryService.Resources(), cls.exampleMD)
        destination_file = os.path.join(DirectoryService.App(), cls.exampleMD)
        cls.__copy_file(source_file, destination_file)
        DataService.AddNewFile(destination_file)
        
        # Example layout
        source_file = os.path.join(DirectoryService.Resources(), cls.exampleLayout)
        destination_file = os.path.join(DirectoryService.App(), cls.exampleLayout)
        cls.__copy_file(source_file, destination_file)
        cls.temp_files.append(destination_file)

        # Example logo
        source_file = os.path.join(DirectoryService.Templates(), cls.defaultLogo)
        destination_file = os.path.join(DirectoryService.App(), cls.defaultLogo)
        cls.__copy_file(source_file, destination_file)
        cls.temp_files.append(destination_file)

        return (cls.exampleMD, cls.exampleLayout, cls.exampleVersion, cls.exampleBuild)

    @classmethod
    def use(cls):
        for filename in os.listdir(DirectoryService.Templates()):
            source_file = os.path.join(DirectoryService.Templates(), filename)
            destination_file = os.path.join(DirectoryService.App(), filename)
            if os.path.isfile(source_file):
                if os.path.exists(destination_file): continue
                shutil.copy2(source_file, destination_file)
                cls.temp_files.append(destination_file)
        return os.path.join(DirectoryService.App(), "layout.html")

    @classmethod
    def clear(cls):
        for temp_file in cls.temp_files:
            if os.path.isfile(temp_file):
                os.remove(temp_file)
        cls.temp_files.clear()