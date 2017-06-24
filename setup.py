from setuptools import setup, find_packages

setup(
    name='mulli',
    version='0.0.7-dev',
    packages=find_packages(),
    include_package_data=True,
    install_requires={
        'Flask==0.11.1',
        'werkzeug==0.11.11',
        'Celery==4.0.2',
    }
)
