@echo off
rem How to run a Python script in a given conda environment from a batch file.

rem Define here the path to your conda installation
set CONDAPATH=C:\Anaconda3

rem Define here the name of the environment
set ENVNAME=cs_opt

rem The following command activates the base environment.
if %ENVNAME%==base (set ENVPATH=%CONDAPATH%) else (set ENVPATH=%CONDAPATH%\envs\%ENVNAME%)

rem Activate the conda environment
call %CONDAPATH%\Scripts\activate.bat %ENVPATH%

rem Run a python script in that environment
python Userinterface.py

rem Deactivate the environment
call conda deactivate
pause>stop