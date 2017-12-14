
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
import json
import dredd_hooks as hooks
from requests import request


INVALID_SPEC_IDS = [
    ('02178c1bcdb25407394348f1ff5273adae287d8ea328184546837957e71c7de57a',
     lambda d: d['account']['publicKey']),

    ('Sawbuck', lambda d: d['asset']['name']),

    ('7ea843aa-1650-4530-94b1-a445d2a8193a', lambda d: d['holding']['id'])
]

ACCOUNT = {
    'email': 'suzie72@suze.au.co',
    'password': '12345',
    'label': 'Susan',
    'description': 'Susan\'s Account'
}

ASSET = {
    'name': 'Suzebuck',
    'description': 'The most valuable currency in the world!',
    'rules': [
        {
            'type': 'OWNER_HOLDINGS_INFINITE'
        },
        {
            'type': 'EXCHANGE_LIMITED_TO_ACCOUNTS',
            'value': ('02178c1bcdb25407394348f1ff5273ada'
                      'e287d8ea328184546837957e71c7de57a')
        }
    ]
}

HOLDING = {
    "label": "Suzebucket",
    "description": "The source for all Suzebucks.",
    "asset": "Suzebuck",
    "quantity": 1337
}


AUTH_ACCOUNT = {
    'email': 'qwerty@suze.au.co',
    'password': '67890'
}


seeded_data = {}


def get_base_api_url(txn):
    protocol = txn.get('protocol', 'http:')
    host = txn.get('host', 'localhost')
    port = txn.get('port', '8000')
    return '{}//{}:{}/'.format(protocol, host, port)

def api_request(method, base_url, path, body=None, auth=None):
    url = base_url + path

    auth = auth or seeded_data.get('auth', None)
    headers = {'Authorization': auth} if auth else None

    response = request(method, url, json=body, headers=headers)
    response.raise_for_status()

    parsed = response.json()
    return parsed.get('data', parsed)


def api_submit(base_url, path, resource, auth=None):
    return api_request('POST', base_url, path, body=resource, auth=auth)


def patch_body(txn, update):
    old_body = json.loads(txn['request']['body'])

    new_body = {}
    for key, value in old_body.items():
        new_body[key] = value
    for key, value in update.items():
        new_body[key] = value

    txn['request']['body'] = json.dumps(new_body)


def sub_nested_strings(dct, pattern, replacement):
    for key in dct.keys():
        if isinstance(dct[key], dict):
            sub_nested_strings(dct[key], pattern, replacement)
        elif isinstance(dct[key], str):
            dct[key] = re.sub(pattern, replacement, dct[key])


@hooks.before_all
def initialize_sample_resources(txns):
    base_url = get_base_api_url(txns[0])
    submit = lambda p, r, a=None: api_submit(base_url, p, r, a)

    # Create ACCOUNT
    account_response = submit('accounts', ACCOUNT)
    seeded_data['auth'] = account_response['authorization']
    seeded_data['account'] = account_response['account']

    # Create ASSET
    seeded_data['asset'] = submit('assets', ASSET)

    # Create HOLDING
    seeded_data['holding'] = submit('holdings', HOLDING)

    # Create AUTH_ACCOUNT
    auth_account_response = submit('accounts', AUTH_ACCOUNT)
    seeded_data['auth_auth'] = auth_account_response['authorization']
    seeded_data['auth_account'] = auth_account_response['account']

    # Replace example auth and identifiers with ones from seeded data
    for txn in txns:
        txn['request']['headers']['Authorization'] = seeded_data['auth']

        for spec_id, id_getter in INVALID_SPEC_IDS:
            sub_nested_strings(txn, spec_id, id_getter(seeded_data))


@hooks.before('/offers > POST > 200 > application/json')
def add_holding(txn):
    patch_body(txn, {
            'source': seeded_data['holding']['id'],
            'target': seeded_data['holding']['id'],
            'targetQuantity': 1337
        })


@hooks.before('/authorization > POST > 200 > application/json')
def add_credentials(txn):
    patch_body(txn, {
        'email': ACCOUNT['email'],
        'password': ACCOUNT['password']
    })


@hooks.before('/holdings > POST > 200 > application/json')
def add_asset_name(txn):
    patch_body(txn, {'asset': seeded_data['asset']['name']})


@hooks.before('/accounts > PATCH > 200 > application/json')
def switch_auth_header(txn):
    txn['request']['headers']['Authorization'] = seeded_data['auth_auth']
