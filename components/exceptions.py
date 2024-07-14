from typing import List

class ParserArgumentException(Exception):

    @property
    def Argument(self):
        return self.__argument
    
    @property
    def Solution(self):
        return self.__solution
    
    def __init__(self, argument, *args: object, solution="") -> None:
        super().__init__(*args)
        self.__argument = argument
        self.__solution = solution
    
    @classmethod
    def Missing(cls, argument):
        message = f"The obligatory argument '{argument}' is missing."
        solution = f"Please provide it with 'comcom --{argument}'"
        return ParserArgumentException(argument, message, solution=solution)
    
    @classmethod
    def MultipleMissing(cls):
        message = f"Multiple arguments are missing:"
        solution = f"Please read the documentation or execute 'comcom --help' for more information."
        return ParserArgumentException("Multiple Arguments", message, solution=solution)

    @classmethod
    def Mismatch(cls, argument, *args):
        args = [str(arg) for arg in args]
        args_str =  ",".join(f" --{arg}" for arg in args)
        message = f"The argument '{argument}' requires the following arguments\n\n{args_str}\n\nto be set as well."
        return ParserArgumentException(argument, message)
    