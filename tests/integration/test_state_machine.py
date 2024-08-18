import json
import logging
import os
from time import sleep
from typing import Dict
from unittest import TestCase
from uuid import uuid4

import boto3
from botocore.client import BaseClient

"""
Make sure env variable AWS_SAM_STACK_NAME exists with the name of the stack we are going to test. 
"""


class TestStateMachine(TestCase):
    """
    This integration test will execute the step function and verify
    - "Record Transaction" is executed
    - the record has been inserted into the transaction record table.
    * The inserted record will be removed when test completed.
    """

    state_machine_arn: str
    transaction_table_name: str

    client: BaseClient
    inserted_record_id: str

    @classmethod
    def get_and_verify_stack_name(cls) -> str:
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")
        if not stack_name:
            raise Exception(
                "Cannot find env var AWS_SAM_STACK_NAME. \n"
                "Please setup this environment variable with the stack name where we are running integration tests."
            )

        # Verify stack exists
        client = boto3.client("cloudformation")
        try:
            client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name}. \n" f'Please make sure stack with the name "{stack_name}" exists.'
            ) from e

        return stack_name

    @classmethod
    def setUpClass(cls) -> None:
        """
        Based on the provided env variable AWS_SAM_STACK_NAME,
        here we use cloudformation API to find out:
        - CRMStateMachine's ARN
        - CRMTable's table name
        """
        stack_name = TestStateMachine.get_and_verify_stack_name()

        client = boto3.client("cloudformation")
        response = client.list_stack_resources(StackName=stack_name)
        resources = response["StackResourceSummaries"]
        state_machine_resources = [
            resource for resource in resources if resource["LogicalResourceId"] == "CRMStateMachine"
        ]
        transaction_table_resources = [
            resource for resource in resources if resource["LogicalResourceId"] == "CRMTable"
        ]
        if not state_machine_resources or not transaction_table_resources:
            raise Exception("Cannot find CRMStateMachine or CRMTable")

        cls.state_machine_arn = state_machine_resources[0]["PhysicalResourceId"]
        cls.transaction_table_name = transaction_table_resources[0]["PhysicalResourceId"]

    def setUp(self) -> None:
        self.client = boto3.client("stepfunctions")

    def tearDown(self) -> None:
        """
        Delete the dynamodb table item that are created during the test
        """
        client = boto3.client("dynamodb")
        for inserted_record_id in self.inserted_record_ids:
            client.delete_item(
                Key={
                    "Email": {
                        "S": inserted_record_id,
                    },
                },
                TableName=self.transaction_table_name,
            )

    def _start_execute(self) -> str:
        """
        Start the state machine execution request and record the execution ARN
        """

        input = [
            {
                'name': 'test 1', 
                'email': 'john.doe@test.com', 
                'optIn': True, 
                'interests': ['datascience', 'python']
            },
            {
                'name': 'test 2', 
                'email': 'john.doe@test.com', 
                'optIn': True, 
                'interests': ['datascience', 'python']
            },
            {
                'name': 'test 3', 
                'email': 'jenny.doe@test.com', 
                'optIn': True, 
                'interests': ['datascience', 'python']
            },
        ]
        
        response = self.client.start_execution(
            stateMachineArn=self.state_machine_arn, name=f"integ-test-{uuid4()}", input=json.dumps(input)
        )
        return response["executionArn"]

    def _wait_execution(self, execution_arn: str):
        while True:
            response = self.client.describe_execution(executionArn=execution_arn)
            status = response["status"]
            if status == "SUCCEEDED":
                logging.info(f"Execution {execution_arn} completely successfully.")
                break
            elif status == "RUNNING":
                logging.info(f"Execution {execution_arn} is still running, waiting")
                sleep(3)
            else:
                self.fail(f"Execution {execution_arn} failed with status {status}")

    def _retrieve_transaction_records_ids(self, execution_arn: str) -> Dict:
        """
        Make sure "Record Transaction" step was reached, and record the input of it.
        """
        response = self.client.get_execution_history(executionArn=execution_arn)
        events = response["events"]
        record_transaction_entered_events = [
            event
            for event in events
            if event["type"] == "TaskStateEntered" and event["stateEnteredEventDetails"]["name"] == "Has Opt In"
        ]

        self.assertTrue(
            record_transaction_entered_events,
            "Cannot find Record Transaction TaskStateEntered event",
        )
        transaction_table_inputs = [json.loads(record_transaction_entered_events["stateEnteredEventDetails"]["input"]) for record_transaction_entered_events in record_transaction_entered_events]
        self.inserted_record_ids = [item['email'] for item in transaction_table_inputs]  # save this ID for cleaning up
        print(self.inserted_record_ids)

    def _verify_transaction_record_written(self):
        """
        Verify that the record jenny.doe@test.com is writen to the database
        """
        client = boto3.client("dynamodb")
        response = client.get_item(
            Key={
                "Email": {
                    "S": "jenny.doe@test.com",
                },
            },
            TableName=self.transaction_table_name,
        )
        self.assertTrue(
            "Item" in response,
            f'Cannot find record with email jenny.doe@test.com',
        )
        item = response["Item"]
        self.assertDictEqual(item["Email"], {"S": "jenny.doe@test.com"})
        self.assertDictEqual(item["Interests"], {"L":  [{'S': 'datascience'}, {'S': 'python'}]})

    def test_state_machine(self):
        execution_arn = self._start_execute()
        self._wait_execution(execution_arn)
        self._retrieve_transaction_records_ids(execution_arn)
        self._verify_transaction_record_written()
