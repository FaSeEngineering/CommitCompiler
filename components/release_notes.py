import os
import markdown2
import shutil
import base64

from weasyprint import HTML
from typing import Dict
from services import DataService, DirectoryService
from .template import Template
from .comcom_cli import ComComCLI, LogLevel

class ReleaseNotes():

    def __init__(self, layoutFile: str, markdownFile: str, version: str, build: str,
                 outputName=None, 
                 docProperties: Dict[str, str] = Template.documentProperties,
                 optionals: Dict[str, str] = Template.exampleOptionals,
                 logo=None,
                 nologo=False,
                 keepHtml=False, ) -> None:

        # HTML layout file (template)
        self.__layoutFile = layoutFile

        # Output file name  
        self.__markdownFile = os.path.join(DirectoryService.App(), markdownFile)

        # Mendatory variables
        self.__version = version
        self.__build = build
        if(not outputName):
            self.__name = f"{os.path.splitext(os.path.basename(markdownFile))[0]}.pdf"
        else:
            self.__name = outputName

        # Document properties
        self.__docProperties = docProperties
        
        # Optional variables
        self.__optionals = optionals

        # Logo
        if(not logo):
            self.__logo = Template.defaultLogo
        else:
            self.__logo = logo

        # No Logo
        self.__noLogo = nologo

        # Debugging features
        self.__keepHtml = keepHtml

    def create(self):
        self.__convertHTML()
        self.__convertPDF()
        self.__clearTemp()

    def __convertHTML(self):

        # Read the Markdown file
        with open(self.__markdownFile, "r") as file:
            markdown_text = file.read()

        # Convert Markdown to HTML
        self.__html_content = markdown2.markdown(markdown_text)

        # Read the HTML template
        with open(self.__layoutFile, "r") as file:
            template = file.read()

        # Insert the converted HTML content into the template
        final_html = self.__add_variables(template) 

        # Save the final HTML to a file
        
        with open(os.path.join(DirectoryService.Build(), "temp.html"), "w") as file:
            file.write(final_html)

    def __convertPDF(self):
        with open(os.path.join(DirectoryService.Build(), "temp.html"), "r") as file:
            html_string = file.read()
        ComComCLI.logSection("Converting to PDF")
        ComComCLI.printSeparator()
        out = os.path.join(DirectoryService.Build(), self.__name)
        ComComCLI.log(LogLevel["INFO"], "Start conversion", f"Building '{out}'.")
        HTML(string=html_string).write_pdf(out, metadata=self.__docProperties)
        DataService.AddNewFile(out)
        ComComCLI.printSeparator()

    def __clearTemp(self):
        if self.__keepHtml:
            htmlFile = os.path.splitext(self.__name)[0] + ".html" 
            shutil.copyfile(
                os.path.join(DirectoryService.Build(), "temp.html"),
                os.path.join(DirectoryService.Build(), htmlFile)
            )
        os.remove(os.path.join(DirectoryService.Build(), "temp.html"))

    def __add_variables(self, template: str):
        
        # Status
        ComComCLI.logSection("Adding variables")
        ComComCLI.printSeparator()

        # Prepare content {{content}}
        content = template.replace("{{content}}", self.__html_content)

        # {{version}}
        content = content.replace("{{version}}", self.__version)
        ComComCLI.log(LogLevel["INFO"], "Set variable", f"version: {self.__version}")

        # {{version}}
        content = content.replace("{{build}}", self.__build)
        ComComCLI.log(LogLevel["INFO"], "Set variable", f"build: {self.__build}")

        # {{doctitle}}
        docTitle = os.path.splitext(self.__name)[0]
        content = content.replace("{{doctitle}}", docTitle)
        ComComCLI.log(LogLevel["INFO"], "Set variable", f"doctitle: {docTitle}")

        # {{date}}
        content = content.replace("{{date}}", DataService.Timestamp())
        ComComCLI.log(LogLevel["INFO"], "Set variable", f"date: {DataService.Timestamp()}")

        # Optional variables
        if self.__optionals:
            for var, value in self.__optionals.items():
                content = content.replace("{{" + var + "}}", value)
                ComComCLI.log(LogLevel["INFO"], "Set variable", f"{var}: {value}")

        # {{logo}}
        image_path = os.path.join(DirectoryService.App(), self.__logo)
        if os.path.exists(image_path) and not self.__noLogo:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
                image_base64 = f"data:image/png;base64,{image_data}"
            content = content.replace("{{logo}}", image_base64)
            ComComCLI.log(LogLevel["INFO"], "Set variable", f"logo (from file): {self.__logo}")

        # Return
        return content
        