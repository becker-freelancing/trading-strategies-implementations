FROM ubuntu:22.04

# Pakete installieren
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk \
    curl \
    git \
    build-essential \
    wget \
    zlib1g-dev \
    && apt-get clean

# Python 3.11 installieren
RUN wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz && \
    tar -xvf Python-3.11.9.tgz && \
    cd Python-3.11.9 && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make altinstall && \
    ln -s /usr/local/bin/python3.11 /usr/local/bin/python3 && \
    ln -s /usr/local/bin/pip3.11 /usr/local/bin/pip3

# Poetry installieren
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Arbeitsverzeichnis setzen
WORKDIR /app

# Poetry abhängigkeiten installieren
COPY zpython/pyproject.toml ./
COPY zpython/poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Dateien kopieren
COPY apps/remote-execution-app/target/remote-execution-app-1.0-SNAPSHOT.jar app.jar
COPY apps/remote-execution-app/target/libs/ libs/

COPY zpython/live_prediction python/live_prediction
COPY zpython/model python/model
COPY zpython/util python/util
COPY zpython/japy_starter.py python/japy_starter.py

# Startskript ausführbar machen
RUN chmod +x start.sh

# Starten
CMD ["./start.sh"]
