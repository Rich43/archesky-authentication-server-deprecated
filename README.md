archesky_authentication_server
==============================

Getting Started
---------------

Rename config_example.ini to config.ini

* Production
    - uvicorn --workers 8 archesky_authentication_server:app
* Development
    - uvicorn --reload archesky_authentication_server:app

