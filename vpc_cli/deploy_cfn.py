import yaml
import json
import time
import boto3
from botocore.config import Config
from inquirer import prompt, Confirm, Text
from datetime import datetime
from dateutil import tz
from prettytable import PrettyTable

from vpc_cli.validators import stack_name_validator


class DeployCfn:
    client = None
    deploy = False
    name = ''
    region = ''

    def __init__(
            self,
            region,
    ):
        self.region = region
        self.ask_deployment()
        self.input_stack_name()
        self.deployment(self.name, region)

    def ask_deployment(self):
        questions = [
            Confirm(
                name='required',
                message='Do you want to deploy using CloudFormation in here?',
                default=True
            )
        ]

        self.deploy = prompt(questions=questions, raise_keyboard_interrupt=True)['required']

    def input_stack_name(self):
        questions = [
            Text(
                name='name',
                message='Type CloudFormation Stack name',
                validate=lambda _, x: stack_name_validator(x, self.region)
            )
        ]

        self.name = prompt(questions=questions, raise_keyboard_interrupt=True)['name']

    def deployment(self, name, region):
        if self.deploy:  # deploy using cloudformation
            self.client = boto3.client('cloudformation', config=Config(region_name=region))
            response = self.client.create_stack(
                StackName=name,
                TemplateBody=self.get_template(),
                TimeoutInMinutes=15,
                Tags=[{'Key': 'Name', 'Value': name}]
            )
            stack_id = response['StackId']
            event_count = 0

            while True:
                # 1. get stack status
                response = self.client.describe_stacks(
                    StackName=name
                )
                stack_status = response['Stacks'][0]['StackStatus']

                if stack_status in ['CREATE_FAILED', 'ROLLBACK_FAILED',
                                    'ROLLBACK_COMPLETE']:  # create failed
                    print()
                    print('\x1b[31m' + 'Failed!' + '\x1b[0m')
                    print()
                    print('\x1b[31m' + 'Please check CloudFormation at here:' + '\x1b[0m')
                    print()
                    print(
                        '\x1b[31m' +
                        'https://{0}.console.aws.amazon.com/cloudformation/home?region={0}#/stacks/stackinfo?stackId={1}'.format(
                            region, stack_id) +
                        '\x1b[0m')
                    break

                elif stack_status == 'CREATE_COMPLETE':  # create complete successful
                    print()
                    self.print_table()
                    print('\x1b[32m' + 'Success!' + '\x1b[0m')

                    break

                else:
                    events = self.client.describe_stack_events(StackName=self.name)['StackEvents']
                    if len(events) > event_count:  # new events
                        for i in range(0, len(events) - event_count):
                            event = ' {:>11} | \x1b[{}{:<27}\x1b[0m | {:<40} | {}'.format(
                                self.get_timestamp(events[i]['Timestamp']),
                                self.get_color(events[i]['ResourceStatus']),
                                events[i]['ResourceStatus'],
                                events[i]['ResourceType'],
                                events[i].get('ResourceStatusReason', ''))
                            print(event)

                            event_count = len(events)

                    time.sleep(1)

        else:
            print('Done!\n\n')
            print('You can deploy VPC using AWS CLI\n\n\n')
            print(
                'aws cloudformation deploy --stack-name {} --region {} --template-file ./template.yaml'.format(
                    name, region))

    def get_template(self):
        with open('template.yaml', 'r') as f:
            content = yaml.full_load(f)

        content = json.dumps(content)

        return content

    def get_timestamp(self, timestamp: datetime):
        return timestamp.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal()).strftime('%I:%M:%S %p')

    def get_color(self, status: str):
        if 'ROLLBACK' in status or 'FAILED' in status:
            return '31m'

        elif 'PROGRESS' in status:
            return '34m'

        elif 'COMPLETE' in status:
            return '32m'

    def print_table(self):
        table = PrettyTable()
        table.set_style(15)
        table.field_names = ['Logical ID', 'Physical ID', 'Type']
        table.vrules = 0
        table.hrules = 1
        table.align = 'l'
        rows = []

        response = self.client.describe_stack_resources(StackName=self.name)['StackResources']

        for resource in response:
            rows.append([resource['LogicalResourceId'], resource['PhysicalResourceId'], resource['ResourceType']])

        rows = sorted(rows, key=lambda x: (x[2], x[0]))
        table.add_rows(rows)
        print(table)
