# panels-gui
Repository for user interface program to display and analyze DFR data.

Download Python 3.8:
1. Check if you have Python 3.8 by running:
```
python --version
```
2. If you do not have Python 3.8, go to https://www.python.org/downloads/ and install it for your operating system.

3. Check that you now have Python 3.8
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
pipenv run panel serve dfr_ui.py
```

To deactivate virtual environment when finished:
```
exit
```
