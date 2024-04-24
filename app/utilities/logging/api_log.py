import logging
from datetime import datetime

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

    incoming_api = IncomingAPI(url=request.url,
                               method=request.method,
                               headers=str(request.headers),
                               body=str(request.get_json(silent=True)) or request.get_data(),
                               r_headers=str(response.headers),
                               r_body=str(response.get_json(silent=True)) or response.get_data(),
                               status_code=str(response.status_code),
                               status=response.status,
                               remote_address=request.remote_addr)
    db.session.add(incoming_api)
    db.session.commit()

    return response
