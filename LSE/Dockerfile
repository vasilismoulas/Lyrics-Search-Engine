ARG VERSION=latest
FROM python:$VERSION

RUN apt-get update \
    && fc-cache -f -v \
    && apt-get install -y default-jdk\
    && apt-get install -y libx11-6 libxext-dev libxrender-dev libxinerama-dev libxi-dev libxrandr-dev libxcursor-dev \
        libxtst-dev tk-dev \
    && rm -rf /var/lib/apt/lists/*
    
# ENV DISPLAY 192.168.1.41:0.0

WORKDIR /usr/lib/jvm
RUN ln -s default-java temurin

WORKDIR /usr/src/pylucene
RUN curl https://downloads.apache.org/lucene/pylucene/pylucene-9.7.0-src.tar.gz \
    | tar -xz --strip-components=1
RUN cd jcc \
    && NO_SHARED=1 JCC_JDK=/usr/lib/jvm/temurin python setup.py install
RUN make all install JCC='python -m jcc' PYTHON=python NUM_FILES=16

WORKDIR /usr/src

RUN rm -rf pylucene

RUN pip install packaging pandas customtkinter CTkTable pillow beautifulsoup4 requests tqdm

COPY main.py /usr/src/main.py

WORKDIR /usr/src/

CMD ["python", "main.py"]