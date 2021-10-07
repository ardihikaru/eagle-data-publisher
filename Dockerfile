# Build: `$ docker build -t 5g-dive/eagle/pubsub:1.0 .`
# Run: `$ docker run --name pub-svc --rm -it --network host 5g-dive/eagle/pubsub:1.0`
# Run: `$ docker run --name sub-svc --rm -it --network host 5g-dive/eagle/pubsub:1.0`
# python3 data_publisher.py -e tcp/localhost:7446 --resize -v /app/videos/customTest_MIRC-Roadside-20s.mp4

# FROM 5g-dive/eagleeye/nvidia-gpu-opencv:2.4
FROM 5g-dive/eagleeye/core-service:2.4
MAINTAINER NCTU Team (mfardiansyah.eed08g@nctu.edu.tw, timothywilliam.cs06g@g2.nctu.edu.tw)

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

COPY requirements.txt /tmp/requirements.txt

RUN pip3 install --upgrade pip

# Install other requirements
RUN pip3 install Cython maturin
RUN pip3 install -r /tmp/requirements.txt

# Install Zenoh
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain nightly
ENV PATH="/root/.cargo/bin:${PATH}"
RUN pip3 install eclipse-zenoh==0.5.0b8

# Folder structure
RUN set -ex \
	&& mkdir -p /app \
	&& mkdir -p /pycore

# Application
COPY ./data_consumer.py /app/data_consumer.py
COPY ./data_publisher.py /app/data_publisher.py
RUN mkdir -p /app/videos
COPY ./data/videos /app/videos
COPY ./pycore /pycore
ENV PYTHONPATH "${PYTHONPATH}:/pycore"

WORKDIR /app
#CMD ["/usr/bin/python3", "./scheduler.py", "-c", "/conf/scheduler/scheduler.conf"]
