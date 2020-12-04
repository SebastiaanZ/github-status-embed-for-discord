FROM python:3.9-slim

COPY requirements.txt .
RUN pip install --target=/app -r requirements.txt

WORKDIR /app
COPY action.yaml github_status_embed/
COPY ./github_status_embed github_status_embed/

ENV PYTHONPATH /app
ENTRYPOINT ["python", "-m", "github_status_embed"]
