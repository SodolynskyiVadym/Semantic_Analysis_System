FROM nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04


ENV DEBIAN_FRONTEND=noninteractive


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    ffmpeg \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*


RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

COPY requirements.txt .


RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

    
COPY download_model.py .

# 3. Запускаємо скрипт. Модель завантажиться і залишиться всередині образу
ENV MODEL_PATH=/app/model
RUN python download_model.py


COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "stt.py"]