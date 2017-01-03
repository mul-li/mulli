from setuptools import setup

setup(
    name='mulli',
    version='0.0.4',
    py_modules=['mulli'],
    install_requires={
        'Flask==0.11.1',
        'werkzeug==0.11.11',
        'Celery==4.0.2',
    }
)
