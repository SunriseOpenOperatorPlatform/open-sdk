import logging
import os

import requests

artifact_manager_host = os.environ["ARTIFACT_MANAGER_ADDRESS"]


def artifact_exists(body):
    logging.info("Contacting Artifact Manager")
    # body = json.dumps(body)
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        artifact_manager_host + "/artefact-exists/", headers=headers, json=body
    )
    return response


def copy_artifact(body):
    logging.info("Submitting artifact to Artifact Manager")
    # body = json.dumps(body)
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        artifact_manager_host + "/copy-artefact", headers=headers, json=body
    )
    return response
