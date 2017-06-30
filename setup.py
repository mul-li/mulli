from setuptools import setup, find_packages

setup(
    name='mulli',
    description='Flask extensions for mul.li services',
    version='0.0.8-dev',
    packages=find_packages(),
    include_package_data=True,
    install_requires={
        'Flask==0.11.1',
        'werkzeug==0.11.11',
        'Celery==4.0.2',
    }
)
