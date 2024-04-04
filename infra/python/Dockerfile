# ベースイメージとしてpython公式
FROM python:latest            
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    cmake \
    git \
    sudo \
    wget \
    vim

# pip install
RUN pip install --upgrade pip
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
# opencvをDockerで使うときに必要なライブラリをインストール
RUN apt -y update && apt -y upgrade
RUN apt-get install -y libgl1-mesa-dev

WORKDIR /work
CMD ["/bin/bash"] 