from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as fh:
    long_description = fh.read()

# with open('requirements.txt') as f:
    # required = f.read().splitlines()

# just a comment to check the unit test
setup(
    name='cs_opt',
    version='2.0.0',
    description='Optimization',
    author='DLR-FK',
    author_email='',
#    packages=find_packages(),
    packages=['cs_opt', 'utils'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://gitlab.dlr.de/cs-opt_student/02_johannes_cs-opt.git',
    python_requires='>=3.8',
    package_dir={
        'cs_opt': 'src/cs_opt',
        'utils': 'src/utils'
    },
    package_data={'': ['../DOE/opti_LHS_database.p']},
    include_package_data=True,
    install_requires=[
        'scipy>=1.6.3',
        'numpy==1.20.2',
        'scikit-learn>=0.24.2',
        'tabulate>=0.8.9',
        'chaospy>=3.3.8',
        'SALib>=1.3.12',
        'pandas>=1.2.4',
        'matplotlib>=3.4.1',
        'openpyxl==3.0.7',
        'latextable>=0.1.1',
        'flake8==3.8.4',
        'pytest==6.2.5',
        'numba>=0.55.1',
        'Jinja2==3.0.3'
    ]
)


