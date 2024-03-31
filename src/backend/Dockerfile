FROM python:3.10

WORKDIR /usr/src/backend
ENV PYTHONPATH /usr/src/

COPY poetry.lock ./
COPY pyproject.toml ./

RUN pip install poetry

RUN poetry export -o requirements.txt

RUN apt-get update && apt-get install -y libgl1-mesa-glx

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]