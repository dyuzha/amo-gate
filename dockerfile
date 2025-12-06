FROM python:3.12 AS builder

RUN apt-get update && apt-get upgrade -y

# Устанавливаем Poetry
RUN python3 -m pip install --no-cache-dir pipx \
    && python3 -m pipx ensurepath \
    && pipx install poetry==2.2.1

ENV PATH="/root/.local/bin:$PATH"

# Устанавливаем плагин poetry
RUN poetry self add poetry-plugin-export

WORKDIR /app

# Копируем только poetry файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Генерируем файл зависимостей: requirements.txt
RUN poetry export --without-hashes --without test -f requirements.txt -o requirements.txt


FROM python:3.12-slim AS prodaction

RUN apt-get update && apt-get upgrade -y

WORKDIR /gate

# Копируем файл зависимостей из BUILD cборки
COPY --from=builder /app/requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --user -r requirements.txt

RUN apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/*

COPY ./src/gate ./gate/
COPY ./src/main.py ./

CMD ["python", "main.py"]
