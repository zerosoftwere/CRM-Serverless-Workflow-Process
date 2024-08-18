
def lambda_handler(payload, context):
    return list({value['email']: value for value in payload}.values())
