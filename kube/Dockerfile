FROM python:3.8
ENV PYTHONUNBUFFERED 1

WORKDIR /project

ADD requirements.txt /project/

RUN pip install -r requirements.txt

COPY . .

# ENV ENV=prod

CMD [ "python", "runner.py"]
