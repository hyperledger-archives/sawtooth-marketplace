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

import logging
from functools import partial
from marketplace_admin.services import api
from marketplace_admin.services import data


LOGGER = logging.getLogger(__name__)


def init_seed_parser(subparsers):
    parser = subparsers.add_parser(
        'seed',
        help='Submits data to the REST API',
        parents=[api.get_parser(), data.get_parser()])
    return parser


def do_seed(opts):
    LOGGER.info('Reading data: %s', opts.data)
    seed_data = data.load(opts.data)

    LOGGER.info('Submitting data to URL: %s', opts.url)
    submit = partial(api.post, opts.url)

    for account in seed_data['ACCOUNTS']:
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
            data.swap_refs(asset, responses)
            responses['ASSETS'].append(submit('assets', asset, auth))

        for holding in account['HOLDINGS']:
            LOGGER.debug('Submitting Holding: %s', holding['label'])
            data.swap_refs(holding, responses)
            responses['HOLDINGS'].append(submit('holdings', holding, auth))

        for offer in account['OFFERS']:
            LOGGER.debug('Submitting Offer: %s', offer['label'])
            data.swap_refs(offer, responses)
            responses['OFFERS'].append(submit('offers', offer, auth))

    LOGGER.info('Data submission complete.')
