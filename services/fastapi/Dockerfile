FROM python:3.11

RUN mkdir /app

WORKDIR /app

COPY requirements.txt .

RUN pip3.11 install -r requirements.txt

COPY . .

RUN chmod a+x src/docker/*.sh