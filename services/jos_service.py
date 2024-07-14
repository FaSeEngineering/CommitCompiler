import json

class JsonObjectService:
    def getSchemaFromStr(schemaStr): 
        return json.loads(schemaStr)
    
    def getEmptyInstance(schema):
        if "type" not in schema:
            raise ValueError("Schema must have a type.")
        
        schema_type = schema["type"]
        
        if schema_type == "object":
            instance = {}
            properties = schema.get("properties", {})
            for key, prop_schema in properties.items():
                instance[key] = JsonObjectService.getEmptyInstance(prop_schema)
            return instance
        elif schema_type == "array":
            items_schema = schema.get("items", {})
            return [JsonObjectService.getEmptyInstance(items_schema)]
        elif schema_type == "string":
            return ""
        elif schema_type == "number" or schema_type == "integer":
            return 0
        elif schema_type == "boolean":
            return False
        else:
            return None