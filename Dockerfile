FROM python

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install virtualenv --user
RUN virtualenv -p pyton venv
RUN pip install -r requirements.txt
COPY . /code/