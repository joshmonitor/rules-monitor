import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def get_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def write_outputs(outputs: dict):
    env_file = os.getenv('GITHUB_OUTPUT')
    if env_file:
        with open(env_file, "a") as f:
            for key, value in outputs.items():
                f.write(f"{key}={value}\n")
