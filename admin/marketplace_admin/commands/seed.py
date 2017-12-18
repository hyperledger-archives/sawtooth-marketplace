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
import yaml
import logging

from marketplace_admin.services import api


LOGGER = logging.getLogger(__name__)
REF_RE = re.compile('^\$REF=(.+)\[(.+):(.+)\]\.(.+)$')


def init_seed_parser(subparsers):
    parser = subparsers.add_parser('seed',
                                   help='Submits data to the REST API',
                                   parents=[api.get_parser()])
    parser.add_argument('-d', '--data',
                        help='The path to the YAML data file',
                        required=True)
    return parser


def do_seed(opts):
    if not opts.data:
        raise RuntimeError('No data file specified, use -d or --data')

    LOGGER.info('Reading data: %s', opts.data)
    data = yaml.load(open(opts.data, 'r'))

    LOGGER.info('Submitting data to URL: %s', opts.url)
    submit = lambda p, b, a=None: api.post(opts.url, p, b, a)

    for account in data['ACCOUNTS']:
        LOGGER.info('Submitting Account: %s', account['label'])
        auth = submit('accounts', account).get('authorization')

        if not auth:
            credentials = {
                'email': account['email'],
                'password': account['password']
            }
            auth = submit('authorization', credentials).get('authorization')

            if not auth:
                LOGGER.warn('No auth token for %s, skipping dependent data',
                            account['label'])
                continue

        responses = {'ASSETS': [], 'HOLDINGS': [], 'OFFERS': []}

        for asset in account['ASSETS']:
            LOGGER.debug('Submitting Asset: %s', asset['name'])
            _swap_references(asset, responses)
            responses['ASSETS'].append(submit('assets', asset, auth))

        for holding in account['HOLDINGS']:
            LOGGER.debug('Submitting Holding: %s', holding['label'])
            _swap_references(holding, responses)
            responses['HOLDINGS'].append(submit('holdings', holding, auth))

        for offer in account['OFFERS']:
            LOGGER.debug('Submitting Offer: %s', offer['label'])
            _swap_references(offer, responses)
            responses['OFFERS'].append(submit('offers', offer, auth))

    LOGGER.info('Data submission complete.')


def _swap_references(resource, responses):
    for key, value in resource.items():
        try:
            match = REF_RE.fullmatch(value)
        except TypeError:
            continue

        if match is None:
            continue

        list_name = match.group(1)
        filter_key = match.group(2)
        filter_value = match.group(3)
        swap_key = match.group(4)

        try:
            swap_value = next(r[swap_key] for r in responses[list_name]
                              if r[filter_key] == filter_value)
        except StopIteration:
            LOGGER.warn('Unable to find match for ref: %s', value)
            continue

        resource[key] = swap_value
