# Sample FunctionGraph-compliant container image
FROM python:3.10-slim

WORKDIR /opt/function

COPY src/ .

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "server.py"]
