from functions.remove_duplicate import app

def test_lambda_handler_with_duplicate():
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
    assert len(result) == 2

def test_lambda_handler_without_duplicate():
    payload = [
        {
            'name': 'xero', 
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
    assert len(result) == 2