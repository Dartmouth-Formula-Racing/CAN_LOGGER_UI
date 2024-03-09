# panels-gui
Repository for user interface program to display and analyze DFR data.

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

activate virtual environment:
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
