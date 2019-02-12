from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ThreatPlaybook',
    version='1',
    packages=[''],
    package_dir={'': 'threat_playbook'},
    # entry_points={
    #     'console_scripts': [
    #         'threat-playbook = threat_playbook:main'
    #     ]
    # },
    url='https://we45.gitbook.io/threatplaybook/',
    license='MIT License',
    author='we45',
    author_email='info@we45.com',
    install_requires=[
        'pyjq==2.3.1',
        'PyYAML==3.13',
        'robotframework==3.1.1',
        'schema==0.6.8',
        'lxml==4.3.0',
        'requests==2.21.0'
    ],
    description='Threat-Models-as Code, An Action-Oriented Threat Modeling and Automation Framework',
    long_description = long_description,
    long_description_content_type='text/markdown',
    include_package_data=True
)