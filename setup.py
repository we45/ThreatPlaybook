from setuptools import setup

setup(
    name='ThreatPlaybook',
    version='0.8',
    packages=[''],
    entry_points={
          'console_scripts': [
              'threat-playbook = threat_playbook:execute_from_command_line'
          ]
    },
    package_dir={'': 'threat_playbook'},
    url='https://we45.gitbook.io/threatplaybook/',
    license='MIT',
    author='we45',
    author_email='info@we45.com',
    description='Threat-Models-as Code, An Action-Oriented Threat Modeling and Automation Framework'
)
