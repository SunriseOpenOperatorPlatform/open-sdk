# -*- coding: utf-8 -*-
##
# This file is part of the Open SDK
#
# Contributors:
#   - Adrián Pino Martínez (adrian.pino@i2cat.net)
#   - César Cajas (cesar.cajas@i2cat.net)
##
import json

from requests import Response

from sunrise6g_opensdk import logger

log = logger.get_logger(__name__)


def build_custom_http_response(
    status_code: int,
    content: str | bytes | dict | list,
    headers: dict = None,
    encoding: str = None,
    url: str = None,
    request=None,
) -> Response:
    response = Response()
    response.status_code = status_code
    if isinstance(content, (dict, list)):
        content = json.dumps(content)
    response._content = content.encode(encoding or "utf-8") if isinstance(content, str) else content
    response.headers.update(headers or {})
    response.encoding = encoding or "utf-8"
    if url:
        response.url = url
    if request:
        response.request = request
    return response
