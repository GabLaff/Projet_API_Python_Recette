FROM python:3.10
LABEL maintainer="gabriel@provider.com"docker
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
CMD [ "python", "app/dao.py" ]
