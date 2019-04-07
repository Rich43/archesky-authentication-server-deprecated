FROM python:latest

WORKDIR /app

COPY . .

RUN python setup.py bdist_wheel

WORKDIR /app/dist

RUN find -maxdepth 1 -type f -name '*.whl' -exec pip install {} \;

WORKDIR /app

EXPOSE 8000/tcp

ENTRYPOINT [ "uvicorn" ]
CMD [ "--workers", "8", "archesky_authentication_server:app" ]
