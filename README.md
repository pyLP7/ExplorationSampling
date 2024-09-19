# cs-opt

## Description

tbd

## Prerequisites

tbd

## Setup

Please follow the steps below to install the necessary python modules on a Windows machine using `pip` (please do not use `conda`):

# a) Windows instructions with the latest python version

1. Create your project folder (e.g. `my_working_dir`)
2. Clone the repository within the path folder you prefer
```
> git clone https://gitlab.dlr.de/cs-opt/cs-opt.git
```
3. Launching the `cmd`, create a virtual environment in the path folder you prefer with `pip`: 
```
> cd <path_your_env>
> python -m venv <env_name>
```
or with `conda`:
```
> conda create --name <env_name> python==3.8.8
```
4. Activate the virtual environment:
```
> <env_name>\scripts\activate
```
5. Go to the repository just cloned and install the required modules from `requirements.txt` with `pip`:
```
> cd <path_to_requirements.txt>
> pip install -r requirements.txt
```

# b) Windows instructions with a specific python release

1. Donwload the desired python release first:
https://www.python.org/downloads/

2. Install the python release just downloaded

3. Create a new virtual environment:
```
> virtualenv --python=<path_to_your_python_.exe> <name_your_venv>
```
4. Activate you virtual environment:
```
> <name_your_venv>\scripts\activate
```
4. Donwload the `.egg` file from the `dist` folder:
https://gitlab.dlr.de/cs-opt_student/02_johannes_cs-opt/-/tree/master/dist

5. Install the `.egg` file:
```
> pip install <name_egg_file>
```

> The script has been successfully tested on Windows 10 with Python 3.8.8
  as well as on Linus Red Hat 7 with Python x.x.x

## Main Contributors

Here you find the main contributors: Pietro Lualdi

## Contributing

Please see [the contribution guidelines](CONTRIBUTING.md) for further information about how to contribute.

## Changes

Please see the [Changelog](CHANGELOG.md) for notable changes.

## License

Please see the file [LICENSE.md](LICENSE.md) for further information about how the content is licensed.
