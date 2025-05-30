# -*- coding: utf-8 -*-
# Common utilities (errors, HTTP helpers) used by the core network interface (network_interface.py).

import requests
from pydantic import BaseModel

from src import logger

log = logger.get_logger(__name__)


def _make_request(method: str, url: str, data=None):
    try:
        headers = None
        if method == "POST" or method == "PUT":
            headers = {
                "Content-Type": "application/json",
                "accept": "application/json",
            }
        elif method == "GET":
            headers = {
                "accept": "application/json",
            }
        response = requests.request(method, url, headers=headers, data=data)
        response.raise_for_status()
        if response.content:
            return response.json()
    except requests.exceptions.HTTPError as e:
        raise CoreHttpError(e) from e
    except requests.exceptions.ConnectionError as e:
        raise CoreHttpError("connection error") from e


# QoD methods
def as_session_with_qos_post(
    base_url: str, scs_as_id: str, model_payload: BaseModel
) -> dict:
    data = model_payload.model_dump_json(exclude_none=True)
    url = as_session_with_qos_build_url(base_url, scs_as_id)
    return _make_request("POST", url, data=data)


def as_session_with_qos_get(base_url: str, scs_as_id: str, session_id: str) -> dict:
    url = as_session_with_qos_build_url(base_url, scs_as_id, session_id)
    return _make_request("GET", url)


def as_session_with_qos_delete(base_url: str, scs_as_id: str, session_id: str):
    url = as_session_with_qos_build_url(base_url, scs_as_id, session_id)
    return _make_request("DELETE", url)


def as_session_with_qos_build_url(
    base_url: str, scs_as_id: str, session_id: str = None
):
    url = f"{base_url}/3gpp-as-session-with-qos/v1/{scs_as_id}/subscriptions"
    if session_id is not None and len(session_id) > 0:
        return f"{url}/{session_id}"
    else:
        return url


# Traffic Influence Methods
def traffic_influence_post(
    base_url: str, scs_as_id: str, model_payload: BaseModel
) -> dict:
    data = model_payload.model_dump_json(exclude_none=True)
    url = traffic_influence_build_url(base_url, scs_as_id)
    return _make_request("POST", url, data=data)


def traffic_influence_delete(base_url: str, scs_as_id: str, session_id: str):
    url = traffic_influence_build_url(base_url, scs_as_id, session_id)
    return _make_request("DELETE", url)


def traffic_influence_put(
    base_url: str, scs_as_id: str, session_id: str, model_payload: BaseModel
) -> dict:
    data = model_payload.model_dump_json(exclude_none=True)
    url = traffic_influence_build_url(base_url, scs_as_id, session_id)
    return _make_request("PUT", url, data=data)


def traffic_influence_build_url(base_url: str, scs_as_id: str, session_id: str = None):
    url = f"{base_url}/3gpp-traffic-influence/v1/{scs_as_id}/subscriptions"
    if session_id is not None and len(session_id) > 0:
        return f"{url}/{session_id}"
    else:
        return url


class CoreHttpError(Exception):
    pass
