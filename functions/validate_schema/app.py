from jsonschema import validate, Draft202012Validator

schema = {
    "type" : "array",
    "items": {
        "type": "object",
        "properties": {
            "name" : {"type" : "string", "minLength": 1},
            "email" : {"type" : "string", "format": "email"},
            "optIn" : {"type" : "boolean"},
            "interests" : {
                "type" : "array",
                "items": {"type": "string", "minLength": 1},
                "minItems": 1,
            },
        },
        "required": [ "name", "email", "optIn", "interests" ],
        "additionalProperties": False
    },
    "minItems": 1,
}


def lambda_handler(payload, context):
    print(payload)
    try:
        validate(instance=payload, schema=schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
        return {'isValid': True}
    except:
        return {'isValid': False}
