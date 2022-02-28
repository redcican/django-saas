# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8.2-slim

COPY . /app
WORKDIR /app

RUN python3 -m venv /opt/env

RUN pip install pip --upgrade
RUN /opt/env/bin/pip install -r requirements.txt
RUN chmod +x entrypoint.sh

CMD [ "/app/entrypoint.sh" ]
