FROM python:3.8
ADD . /Woonnet
WORKDIR /Woonnet
VOLUME /woonnet_volume
RUN apt-get update
RUN apt-get -y install libnss3 chromium default-jdk nano
RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "./main.py" ]
ENV TZ=Europe/Amsterdam
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN chmod a+x chromedriver