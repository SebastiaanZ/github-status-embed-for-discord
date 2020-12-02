FROM python:3.9-slim as builder

COPY requirements.txt .

RUN pip install --target=/app -r requirements.txt

FROM gcr.io/distroless/python3-debian10
COPY --from=builder /app /app


WORKDIR /app
COPY ./github_status_embed github_status_embed/

ENV PYTHONPATH /app
CMD ["/app/main.py"]

ENTRYPOINT ["python", "-m", "github_status_embed"]
