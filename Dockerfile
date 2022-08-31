FROM python:3.9-slim

COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

COPY . code/donquijote
WORKDIR code/donquijote
RUN pip3 install -e .

CMD ./start.sh