from functions.validate_schema import app

def test_lambda_handler_with_valid_schema():
    payload = [
        {
            'name': 'xero', 
            'email': 'john.doe@test.com', 
            'optIn': True, 
            'interests': ['datascience', 'python']
        },
        {
            'name': 'alhassan', 
            'email': 'john.doe@test.com', 
            'optIn': True, 
            'interests': ['datascience', 'python']
        },
        {
            'name': 'alhassan', 
            'email': 'jenny.doe@test.com', 
            'optIn': True, 
            'interests': ['datascience', 'python']
        },
    ]
    result = app.lambda_handler(payload, None)
    assert result['isValid'] == True

def test_lambda_handler_with_invalid_schema():
    payload = [
        {
            'names': 'xero', 
            'email': 'john.doe@test.com', 
            'optIn': True, 
            'interests': ['datascience', 'python']
        },
        {
            'name': 'alhassan', 
            'email': 'jenny.doe@test.com', 
            'optIn': True, 
            'interests': ['datascience', 'python']
        },
    ]
    result = app.lambda_handler(payload, None)
    assert result['isValid'] == False

def test_lambda_handler_with_missing_field():
    payload = [
        {
            'name': 'xero', 
            'optIn': True, 
            'interests': ['datascience', 'python']
        },
        {
            'name': 'alhassan', 
            'email': 'jenny.doe@test.com', 
            'optIn': True, 
            'interests': ['datascience', 'python']
        },
    ]
    result = app.lambda_handler(payload, None)
    assert result['isValid'] == False