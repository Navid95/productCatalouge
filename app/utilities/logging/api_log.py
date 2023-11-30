import logging
from datetime import datetime

from flask import g
from flask import request
from flask import Response

from environ import API_LOGGER_NAME
from environ import APP_LOGGER_NAME

app_logger = logging.getLogger(APP_LOGGER_NAME)
api_logger = logging.getLogger(API_LOGGER_NAME)


def get_request_time():
    request_time = datetime.now().isoformat()
    setattr(g, 'request_time', request_time)


def log_api_call(response: Response):
    response_time = datetime.now().isoformat()
    request_time = getattr(g, 'request_time')
    request_data = request.data
    response_data = response.data
    message = {
        "request_time": request_time,
        "response_time": response_time,
        "request_data": request_data,
        "response_data": response_data
    }
    api_logger.info(msg=message)
    app_logger.info(msg=message)
    return response
