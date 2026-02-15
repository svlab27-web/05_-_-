FROM python:3.11-slim

WORKDIR /app

# системные зависимости для сборки psutil
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# сначала зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# потом код
COPY . /app

CMD ["python", "-m", "src.agents.agent_4.agent"]


