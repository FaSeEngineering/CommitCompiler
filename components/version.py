import os
from typing import Any
import json
import jsonschema
from jsonschema import validate
from .comcom_cli import ComComCLI, LogLevel
from services import JsonObjectService, DirectoryService, DataService

class Version():

    # Data Property
    @property
    def Data(self):
        return self.__data
    @Data.setter
    def Data(self, value):
        self.__data = value

    # Constructor
    def __init__(self, version, buildnumber, outputName="vInfo.json") -> None:
        
        schemaFile = os.path.join(DirectoryService.Resources(), "comcomSchema.json")
        with open(schemaFile, "r") as file:
            schema = file.read()
        self.__schema = schema
        jsonSchema = JsonObjectService.getSchemaFromStr(self.__schema)
        self.__data = JsonObjectService.getEmptyInstance(jsonSchema)
        self.__data["version"] = version
        self.__data["buildNumber"] = buildnumber
        self.__name = outputName
        
    def __trim(d):
        if isinstance(d, dict):
            return {k: Version.__trim(v) for k, v in d.items() if not Version.__is_empty(v)}
        elif isinstance(d, list):
            return [Version.__trim(item) for item in d if not Version.__is_empty(item)]
        else:
            return d

    def __is_empty(value):
        if value in ("", [], {}, None):
            return True
        if isinstance(value, dict):
            return all(Version.__is_empty(v) for v in value.values())
        if isinstance(value, list):
            return all(Version.__is_empty(item) for item in value)
        return False
    
    def create(self):

        # Status
        ComComCLI.logSection("Building vInfo.json")
        ComComCLI.printSeparator()
        
        # Timestamp
        self.__data["buildDate"] = DataService.Timestamp()
        ComComCLI.log(LogLevel["INFO"], "Adding built timestamp", f"{DataService.Timestamp()} to file.")

        # Create data
        if(self.__data == {}): raise "No data provided."
        trimmed = Version.__trim(self.__data)
        file = os.path.join(DirectoryService.App(), self.__name)
        with open(file, "w") as json_file:
            json.dump(trimmed, json_file)
        DataService.AddNewFile(file)

        ComComCLI.log(LogLevel["INFO"], "vInfo.json completed", f"Successfully built '{self.__name}'")
