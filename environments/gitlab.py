import os
from typing import Union, List
from services import DirectoryService, DataService
from components import ReleaseNotes, Version, ComComCLI, LogLevel
from .environment import GitEnvironment

class GitLab(GitEnvironment):

    # Constructor
    def __init__(self) -> None:
        super().__init__()

    # Global Pipeline
    def use(self, layout, notes="ReleaseNotes.md", vInfoOutputName="vInfo.json", **kwargs):

        # Print
        ComComCLI.printHeadline("GitLab", "Using the CommitCompiler GitLab Workflow")

        # Inform Directory Service
        DirectoryService.UseGitLab()

        # Prepare Repository
        ComComCLI.logSection("Prepare Repository")
        ComComCLI.printSeparator()
        self.configure()
        self.initializeRepository()

        # Create or Update .md file
        ComComCLI.logSection("Create / Update file contents")
        ComComCLI.printSeparator()
        file_path = os.path.join(DirectoryService.App(), notes)
        self.appendReleaseNotes(file_path)
        ComComCLI.log(LogLevel["INFO"], "Updating", f"Adding git tag and tag message to file: {notes}")
        DataService.AddNewFile(file_path)

        # Create Release Notes
        releaseNotes = ReleaseNotes(layout, notes, 
                             self.getVariable("CI_COMMIT_TAG"), 
                             self.getVariable("CI_COMMIT_SHORT_SHA"), 
                             **kwargs
                            )
        releaseNotes.create()        

        # vInfo.json
        version = Version(
            self.getVariable("CI_COMMIT_TAG"), 
            self.getVariable("CI_COMMIT_SHORT_SHA"),
            outputName=vInfoOutputName
        )
        version.create()

        # Commit and Push
        ComComCLI.logSection("Save and Commit Changes")
        ComComCLI.printSeparator()
        self.addCommitAndPush([os.path.join(DirectoryService.App(), notes), 
                               os.path.join(DirectoryService.App(), vInfoOutputName)])

    # Create Release Notes: markdown file
    def appendReleaseNotes(self, file_path):
        notes = f"# {self.getVariable("CI_COMMIT_TAG")}\n\n{self.getVariable("CI_COMMIT_TAG_MESSAGE")}"
        self.__append_release_notes(file_path, notes)

    def __append_release_notes(self, file_path: str, content):
        try:
            with open(file_path, "r") as file:
                original_contents = file.readlines()
        except FileNotFoundError:
            original_contents = []
        new_contents = [content + "\n"] + original_contents
        with open(file_path, "w") as file:
            file.writelines(new_contents)
    
    # GitLab Pipeline
    def configure(self, email="comcom@fase-engineering.com", author="CommitCompiler"):
        commands = { 
            "configure email": self.command("config.email", email=email),
            "configure author": self.command("config.author", author=author) 
        }
        self.execute(commands)

    def initializeRepository(self):
        commands = { 
            "git remote": self.command("remote", 
                                   server=self.getVariable("CI_SERVER_HOST"), 
                                   path=self.getVariable("CI_PROJECT_PATH")
                                ),
            "git fetch": self.command("fetch"),
            "git checkout": self.command("checkout", branch=self.getVariable("CI_DEFAULT_BRANCH")),
        }
        self.execute(commands)

    def addCommitAndPush(self, files: Union[str, List[str]]):

        # Craft add command
        add_cmd = self.command("add")

        # Single file
        if isinstance(files, str):
            add_cmd.append(files)

        # Multiple files
        elif isinstance(files, list):
            add_cmd.extend(files)
        
        # Craft commands and execute
        commands = { 
            "git add": add_cmd,
            "git commit": self.command("commit", message=self.DefaultCommitMessage), 
            "git push": self.command("push", branch=self.getVariable("CI_DEFAULT_BRANCH"))
        }
        self.execute(commands)

    