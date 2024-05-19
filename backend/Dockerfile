FROM python:3.10

WORKDIR /usr/backend
ENV PYTHONPATH /usr/backend/src

COPY poetry.lock ./
COPY pyproject.toml ./

RUN apt-get update && apt-get install -y libgl1-mesa-glx
RUN pip install poetry
RUN poetry install --no-interaction --no-ansi

COPY . .

CMD ["poetry", "run", "uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]