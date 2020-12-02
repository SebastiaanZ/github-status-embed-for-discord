FROM python:3.9-slim

ENV PIP_NO_CACHE_DIR=false

# Copy requirements file first so we can skip so we can skip
# rebuilding the layers that install dependencies unless the
# requirements change.
COPY requirements.txt .

RUN pip install -U -r requirements.txt

WORKDIR /action

COPY ./github_status_embed/* ./github_status_embed/

ENTRYPOINT ["python", "-m", "github_status_embed"]
