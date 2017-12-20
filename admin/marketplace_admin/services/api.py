# Copyright 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------------

import re
import logging
import requests
from functools import partial
from argparse import ArgumentParser


LOGGER = logging.getLogger(__name__)


def get_parser():
    parser = ArgumentParser(add_help=False)
    parser.add_argument('-u', '--url',
                    help='The url of the REST API to send requests to',
                    default='http://localhost:8000')
    return parser


def request(method, base_url, path, body=None, auth=None):
    base_url = base_url if re.search('://', base_url) else 'http://' + base_url
    url = '{}/{}'.format(base_url, path)
    headers = {'Authorization': auth} if auth else None

    response = requests.request(method, url, json=body, headers=headers)
    response_body = response.json()

    if response.status_code > 299:
        LOGGER.warn('%s request failed to path: %s', method, path)
        LOGGER.warn('%s %s: %s',
                    response.status_code,
                    response.reason,
                    response_body.get('error'))

    return response_body

get = partial(request, 'GET')
post = partial(request, 'POST')
patch = partial(request, 'PATCH')
