# CUDA-basiertes Image mit PyTorch
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Setz dein Name hier
LABEL maintainer="deinname@example.com"

# Systempakete
RUN apt-get update && apt-get install -y \
    python3 python3-pip git && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis
WORKDIR /workspace

# Requirements installieren
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Code hinzufügen
COPY . .

# Entrypoint-Skript kopieren
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Entrypoint setzen (leitet Parameter durch)
ENTRYPOINT ["/entrypoint.sh"]

# Standardkommando (kann überschrieben werden)
CMD ["python", "training/test/torch_gpu_test.py"]
