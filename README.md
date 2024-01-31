# panels-gui
Repository for user interface program to display and analyze DFR data.

Set up virtual environment:
```
python -m venv env
```

activate virtual environment on Linux:
```
source env/bin/activate
```
activate virtual environment on Windows:
```
.\env\Scripts\activate
```

To install packages needed:
```
pip install -r requirements.txt
```

To run the project, go to the project in terminal and run:
```
panel serve dfr_ui.py
```
For auto reload and automatic pop-up use:
```
panel serve dfr_ui.py --autoreload --show
```

To deactivate virtual environment when finished:
```
deactivate
```
