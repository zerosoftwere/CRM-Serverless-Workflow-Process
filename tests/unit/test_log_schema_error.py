from functions.log_schema_error import app
from unittest import mock

def test_log_error_to_cloudwatch():
    event = {'payload':'test', 'logGroupName': 'test', 'logStreamName': 'test'}
    with mock.patch('functions.log_schema_error.app.client') as mock_client:
        app.lambda_handler(event, None)
        mock_client.put_log_events.assert_called_once()
