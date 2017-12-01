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
import time
import unittest
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from uuid import uuid4

from sawtooth_cli.rest_client import RestClient

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory

from marketplace_transaction import transaction_creation


LOGGER = logging.getLogger(__name__)


def make_key():
    context = create_context('secp256k1')
    private_key = context.new_random_private_key()
    signer = CryptoFactory(context).new_signer(private_key)
    return signer


REST_URL = 'rest-api:8008'


BATCH_KEY = make_key()


class BlockchainTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        wait_for_rest_apis([REST_URL])
        cls.client = MarketplaceClient(REST_URL)

        cls.key1 = make_key()

    def test_00_create_account(self):
        """Tests the CreateAccount validation rules.

        Notes:
            CreateAccount validation rules
                - The public_key is unique for all accounts.
        """

        self.assertEqual(
            self.client.create_account(
                key=self.key1,
                label=uuid4().hex,
                description=uuid4().hex)[0]['status'],
            "COMMITTED")

        self.assertEqual(
            self.client.create_account(
                key=self.key1,
                label=uuid4().hex,
                description=uuid4().hex)[0]['status'],
            "INVALID",
            "There can only be 1 account per public key.")


class MarketplaceClient(object):

    def __init__(self, url):
        self._client = RestClient(base_url="http://{}".format(url))

    def create_account(self, key, label, description):
        batch_list, signature = transaction_creation.create_account(
            txn_key=key,
            batch_key=BATCH_KEY,
            label=label,
            description=description)
        self._client.send_batches(batch_list)
        return self._client.get_statuses([signature], wait=10)


def wait_until_status(url, status_code=200, tries=5):
    """Pause the program until the given url returns the required status.
    Args:
        url (str): The url to query.
        status_code (int, optional): The required status code. Defaults to 200.
        tries (int, optional): The number of attempts to request the url for
            the given status. Defaults to 5.
    Raises:
        AssertionError: If the status is not received in the given number of
            tries.
    """
    attempts = tries
    while attempts > 0:
        try:
            response = urlopen(url)
            if response.getcode() == status_code:
                return

        except HTTPError as err:
            if err.code == status_code:
                return

            LOGGER.debug('failed to read url: %s', str(err))
        except URLError as err:
            LOGGER.debug('failed to read url: %s', str(err))

        sleep_time = (tries - attempts + 1) * 2
        LOGGER.debug('Retrying in %s secs', sleep_time)
        time.sleep(sleep_time)

        attempts -= 1

    raise AssertionError(
        "{} is not available within {} attempts".format(url, tries))


def wait_for_rest_apis(endpoints, tries=5):
    """Pause the program until all the given REST API endpoints are available.
    Args:
        endpoints (list of str): A list of host:port strings.
        tries (int, optional): The number of attempts to request the url for
            availability.
    """
    for endpoint in endpoints:
        http = 'http://'
        url = endpoint if endpoint.startswith(http) else http + endpoint
        wait_until_status(
            '{}/blocks'.format(url),
            status_code=200,
            tries=tries)