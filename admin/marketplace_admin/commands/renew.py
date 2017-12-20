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


def init_renew_parser(subparsers):
    parser = subparsers.add_parser(
        'renew',
        help='Closes and reopens any "renewable" Offers',
        parents=[api.get_parser(), data.get_parser()])
    return parser


def do_renew(opts):
    LOGGER.info('Reading data: %s', opts.data)
    renew_data = data.load(opts.data)

    LOGGER.info('Submitting data to URL: %s', opts.url)
    fetch = partial(api.get, opts.url)
    submit = partial(api.post, opts.url)
    update = partial(api.patch, opts.url)

    LOGGER.debug('Fetching all existing open offers')
    open_offers = [o for o in fetch('offers') if o['status'] == 'OPEN']

    for account in renew_data['ACCOUNTS']:
        LOGGER.info('Authenticating as Account: %s', account['label'])
        credentials = {
            'email': account['email'],
            'password': account['password']
        }
        auth = submit('authorization', credentials).get('authorization')

        if not auth:
            LOGGER.warn('No auth token for %s, skipping dependent data',
                        account['label'])
            continue

        LOGGER.debug('Fetching current account info for: %s', account['label'])
        public_key = data.parse_jwt(auth)['public_key']
        account_data = fetch('accounts/{}'.format(public_key))

        if account_data.get('error'):
            LOGGER.warn('No account data for %s, skipping dependent data',
                        account['label'])
            continue

        account_offers = [o for o in open_offers
                          if account_data['publicKey'] in o['owners']]

        for renewable in account['RENEWABLES']:
            data.swap_refs(renewable, account_data)

            matching_offers = [o for o in account_offers
                               if renewable['label'] == o.get('label')
                               and renewable['source'] == o['source']]

            for match in matching_offers:
                LOGGER.debug('Closing matching offer: %s', match['id'])
                update('offers/{}/close'.format(match['id']), None, auth)

            LOGGER.debug('Submitting new offer: %s', renewable['label'])
            submit('offers', renewable, auth)

    LOGGER.info('Renewals complete.')
