# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8.2-slim

# Section 2- Python Interpreter Flags
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
# Section 3- Compiler and OS libraries
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app
RUN python3 -m venv /opt/venv

RUN /opt/venv/bin/pip install pip --upgrade && \
    /opt/venv/bin/pip install -r requirements.txt && \
 chmod 755 entrypoint.sh

CMD [ "/app/entrypoint.sh" ]
