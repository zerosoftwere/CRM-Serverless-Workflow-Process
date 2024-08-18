from jsonschema import validate

schema = {
    "type" : "array",
    "items": {
        "type": "object",
        "properties": {
            "name" : {"type" : "string"},
            "email" : {"type" : "string"},
            "optIn" : {"type" : "boolean"},
            "interests" : {
                "type" : "array",
                "items": {"type": "string"},
            },
        },
        "required": [ "name", "email", "optIn", "interests" ],
        "additionalProperties": False
    }
}


def lambda_handler(payload, context):
    print(payload)
    try:
        validate(instance=payload, schema=schema)
        return {'isValid': True}
    except:
        return {'isValid': False}
