FROM ghcr.io/astral-sh/uv:python3.12-alpine

ADD . /publisher

WORKDIR /publisher

RUN uv sync --frozen 

CMD ["uv", "run", "main.py"] 