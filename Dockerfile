FROM python:3.8.8

WORKDIR /CANgui
COPY requirements.txt /CANgui/
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . /CANgui/

CMD ["panel", "serve", "dfr_ui.py"]