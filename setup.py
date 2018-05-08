from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ThreatPlaybook',
    version='0.95',
    packages=['threat_playbook'],
    entry_points={
        'console_scripts': [
            'threat-playbook = threat_playbook:execute_from_command_line'
        ]
    },
    url='https://we45.gitbook.io/threatplaybook/',
    license='LGPL',
    author='we45',
    author_email='info@we45.com',
    install_requires=[
        'mongoengine==0.15.0',
        'pathlib==1.0.1',
        'PyYAML==3.12',
        'robotframework==3.0.4'
    ],
    description='Threat-Models-as Code, An Action-Oriented Threat Modeling and Automation Framework',
    long_description = long_description,
    long_description_content_type='text/markdown'
)
