FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY data ./data
COPY examples ./examples
COPY scripts ./scripts

RUN pip install --no-cache-dir -e ".[dev,api,mcp,live]"

ENV AQTC_STRIPE_MODE=mock
ENV AQTC_NVIDIA_MODE=mock
ENV AQTC_DISABLE_HERMES_ENV=true

CMD ["aqtc", "demo"]
