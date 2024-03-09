# panels-gui
Repository for user interface program to display and analyze DFR data.

Download Python 3.8:
1. Check if you have Python 3.8 by running:
```
python --version
```
2. If you do not have Python 3.8, follow the instructions here (https://github.com/pyenv/pyenv?tab=readme-ov-file#installation) to install pyenv. Pyenv makes it easy to switch between python versions on your system. If you already know how to switch between versions, you can download Python 3.8 here (https://www.python.org/downloads/) and skip the pyenv-related steps. Alternatively, you can use conda or any other method to install Python 3.8.
  
3. Once you've installed pyenv, run:
```
pyenv install 3.8
```

4. Set Python 3.8 as the global version:
```
pyenv global 3.8
```
To switch back to other versions of Python, run pyenv global followed by the version number.

5. Verify that you are using Python 3.8:
```
python --version
```

Set up directory:
1. Download files and folders from this Git repository and store them in a folder of your choice. This is your directory folder.

2. Ensure that the "Pipfile" and "Pipfile.lock" files are in this folder.


Set up virtual environment:
1. Make sure you have pipenv
```
pip install pipenv
```
2. Create the virtual environment
Set up virtual environment:
```
pipenv install
```

Activate virtual environment:
```
pipenv shell
```

To run the project, while in your directory folder, run the following line:
```
pipenv run panel serve --show dfr_ui.py
```
Press `CTRl` + `C` to stop running the application

To deactivate virtual environment when finished:
```
exit
```
