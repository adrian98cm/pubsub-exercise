FROM ghcr.io/astral-sh/uv:python3.12-alpine

ADD . /subscriber

WORKDIR /subscriber

RUN apk add --no-cache libpq postgresql-dev gcc musl-dev

RUN uv sync --frozen 

CMD ["uv", "run", "main.py"] 