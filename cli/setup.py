from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='ThreatPlaybook-Client',
    version='3.0.2',
    packages=['playbook'],
    entry_points={
        'console_scripts': [
            'playbook = playbook:main'
        ]
    },
    url='https://we45.github.io/threatplaybook/',
    license='MIT License',
    author='we45',
    author_email='info@we45.com',
    install_requires=[
        'docopt',
        'requests',
        'huepy',
        'pickledb',
        'pyyaml',
        'pyjq',
        "jinja2",
        "tabulate"
    ],
    description='Client for ThreatPlaybook that allows a user to interacts with the ThreatPlaybook API',
    include_package_data=True
)