from setuptools import setup, find_packages

requires = [
    'ansicon==1.89.0',
    'blessed==1.19.1',
    'boto3==1.26.41',
    'botocore==1.29.41',
    'colorama==0.4.6',
    'inquirer==2.10.0',
    'ipaddr==2.2.0',
    'jinxed==1.2.0',
    'jmespath==1.0.1',
    'prettytable==3.4.1',
    'psutil==5.9.4',
    'ptyprocess==0.7.0',
    'pyfiglet==0.8.post1',
    'python-dateutil==2.8.2',
    'python-editor==1.0.4',
    'pytz==2022.7',
    'pywin32==305',
    'PyYAML==6.0',
    'readchar==4.0.3',
    's3transfer==0.6.0',
    'six==1.16.0',
    'tqdm==4.64.1',
    'urllib3==1.26.13',
    'wcwidth==0.2.5',
    'wexpect==4.0.0',
]

setup(
    name='aws-vpc-cli',
    version='0.2.1',
    author='marcus16-kang',
    description='AWS VPC CloudFormation Stack Generator',
    author_email='marcus16-kang@outlook.com',
    license='MIT',
    entry_points={
        'console_scripts': [
            'vpc-cli=vpc_cli.main:main'
        ]
    },
    install_requires=requires,
    # packages=find_packages(),
    python_requires='>=3.7',
    url='https://github.com/marcus16-kang/vpc-stack-generator-cli',
    project_urls={
        'Source': 'https://github.com/marcus16-kang/vpc-stack-generator-cli'
    }
)
