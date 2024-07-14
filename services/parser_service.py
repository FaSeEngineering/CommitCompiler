class ParserService:
    
    @classmethod
    def parseVariables(cls, args):
        variables = {}
        for var in args.set:
            key_value = var.split("=", 1)
            if len(key_value) == 2:
                variables[key_value[0]] = key_value[1]
            else:
                raise ValueError(f"Invalid variable assignment: {var}")
        
        return variables