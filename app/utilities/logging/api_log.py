import logging
from datetime import datetime
from copy import deepcopy

from flask import g
from flask import request
from flask import Response

from app.models.log import IncomingAPI
from environ import API_LOGGER_NAME
from environ import APP_LOGGER_NAME
from app.extensions import db

app_logger = logging.getLogger(APP_LOGGER_NAME)
api_logger = logging.getLogger(API_LOGGER_NAME)


def get_request_time():
    request_time = datetime.now()
    setattr(g, 'request_time', request_time)


def log_api_call(response: Response):
    response_time = datetime.now()
    request_time = getattr(g, 'request_time')
    message = {
        'url': request.url,
        'method': request.method,
        'status_code': str(response.status_code),
        'status': response.status,
        'headers': str(request.headers),
        'body': str(request.get_json(silent=True)) or request.get_data(),
        'r_body': str(response.get_json(silent=True)) or response.get_data(),
        'r_headers': str(response.headers),
        'request_time': request_time,
        'response_time': response_time,
        'remote_address': request.remote_addr
    }

    file_message = deepcopy(message)
    file_message['request_time'] = request_time.isoformat()
    file_message['response_time'] = response_time.isoformat()
    api_logger.info(msg=message)
    app_logger.info(msg=message)

    incoming_api = IncomingAPI(**message)
    db.session.add(incoming_api)
    db.session.commit()

    return response
