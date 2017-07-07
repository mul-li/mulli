from setuptools import setup, find_packages

setup(
    name='mulli',
    description='Flask extensions for mul.li services',
    version='0.0.8-dev',
    packages=find_packages(),
    include_package_data=True,
    install_requires={
        'Flask==0.12.2',
        'Celery==4.0.2',
    }
)
