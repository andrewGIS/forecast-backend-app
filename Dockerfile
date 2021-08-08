FROM osgeo/gdal:ubuntu-small-latest

WORKDIR /flask-app

COPY . .

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    python3.8 python3-pip

RUN pip3 install -r requirements.txt

RUN pip3 install gunicorn[gevent]