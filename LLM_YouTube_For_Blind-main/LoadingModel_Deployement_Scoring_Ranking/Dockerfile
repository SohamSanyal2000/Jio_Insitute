FROM python:3.10

WORKDIR /data
COPY . /data
RUN pip install -r requirements.txt

COPY . .

CMD [ "uvicorn", "sample_rest_server:app", "--host", "0.0.0.0", "--port", "5500" ]