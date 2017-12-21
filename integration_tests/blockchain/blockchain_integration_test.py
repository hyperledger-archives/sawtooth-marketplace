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

from sawtooth_rest_api.protobuf import batch_pb2

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

        cls.signer1 = make_key()
        cls.signer2 = make_key()
        cls.sawbucks = uuid4().hex
        cls.pickles = uuid4().hex
        cls.signer1_sawbucks = str(uuid4())
        cls.signer1_pickles = str(uuid4())
        cls.signer2_sawbucks = str(uuid4())
        cls.signer2_pickles = str(uuid4())
        cls.sawbucks_for_pickles = str(uuid4())
        cls.pickles_for_sawbucks = str(uuid4())

    def test_00_create_account(self):
        """Tests the CreateAccount validation rules.

        Notes:
            CreateAccount validation rules
                - The public_key is unique for all accounts.
        """

        self.assertEqual(
            self.client.create_account(
                key=self.signer1,
                label=uuid4().hex,
                description=uuid4().hex)[0]['status'],
            "COMMITTED")

        self.assertEqual(
            self.client.create_account(
                key=self.signer1,
                label=uuid4().hex,
                description=uuid4().hex)[0]['status'],
            "INVALID",
            "There can only be 1 account per public key.")

        self.assertEqual(
            self.client.create_account(
                key=self.signer2,
                label=uuid4().hex,
                description=uuid4().hex)[0]['status'],
            "COMMITTED")

    def test_01_create_asset(self):
        """Tests the CreateAsset validation rules

        Notes:
            CreateAsset validation rules
                - The Txn signer has an account
                - There is not already an Asset with the same name.
        """

        self.assertEqual(
            self.client.create_asset(
                key=self.signer1,
                name=self.sawbucks,
                description=uuid4().hex,
                rules=[])[0]['status'],
            "COMMITTED")

        self.assertEqual(
            self.client.create_asset(
                key=self.signer1,
                name=self.sawbucks,
                description=uuid4().hex,
                rules=[])[0]['status'],
            "INVALID",
            "There must not be another Asset with the same name")

        invalid_signer = make_key()
        self.assertEqual(
            self.client.create_asset(
                key=invalid_signer,
                name=uuid4().hex,
                description=uuid4().hex,
                rules=[])[0]['status'],
            "INVALID",
            "The txn signer must have an account.")

        self.assertEqual(
            self.client.create_asset(
                key=self.signer2,
                name=self.pickles,
                description=uuid4().hex,
                rules=[])[0]['status'],
            "COMMITTED")

    def test_02_create_holding(self):
        """Tests the CreateHolding validation rules.

        Notes:
            CreateHolding validation rules
                - The Holding id must not already belong to a holding.
                - The txn signer must own an Account.
                - The asset must exist.
                - If the quantity is not 0, then the txn signer must
                  be an owner of the asset.
        """

        self.assertEqual(
            self.client.create_holding(
                key=self.signer1,
                identifier=self.signer1_sawbucks,
                label=uuid4().hex,
                description=uuid4().hex,
                asset=self.sawbucks,
                quantity=2)[0]['status'],
            "COMMITTED")

        self.assertEqual(
            self.client.create_holding(
                key=self.signer1,
                identifier=self.signer1_sawbucks,
                label=uuid4().hex,
                description=uuid4().hex,
                asset=self.sawbucks,
                quantity=3)[0]['status'],
            "INVALID",
            "The Holding Id must not already belong to a holding.")

        no_account = make_key()

        self.assertEqual(
            self.client.create_holding(
                key=no_account,
                identifier=str(uuid4()),
                label=uuid4().hex,
                description=uuid4().hex,
                asset=self.sawbucks,
                quantity=2)[0]['status'],
            "INVALID",
            "The Account must exist.")

        self.assertEqual(
            self.client.create_holding(
                key=self.signer2,
                identifier=str(uuid4()),
                label=uuid4().hex,
                description=uuid4().hex,
                asset=self.sawbucks,
                quantity=2)[0]['status'],
            "INVALID",
            "The account must be owned by the txn signer.")

        self.assertEqual(
            self.client.create_holding(
                key=self.signer1,
                identifier=str(uuid4()),
                label=uuid4().hex,
                description=uuid4().hex,
                asset=uuid4().hex,
                quantity=3)[0]['status'],
            "INVALID",
            "The Asset/holding must exist")

        self.assertEqual(
            self.client.create_holding(
                key=self.signer2,
                identifier=str(uuid4()),
                label=uuid4().hex,
                description=uuid4().hex,
                asset=self.sawbucks,
                quantity=2)[0]['status'],
            "INVALID",
            "The asset/holding must be owned by the txn signer if the "
            "quantity of the Holding is not zero.")

        self.assertEqual(
            self.client.create_holding(
                key=self.signer1,
                identifier=self.signer2_sawbucks,
                label=uuid4().hex,
                description=uuid4().hex,
                asset=self.pickles,
                quantity=0)[0]['status'],
            "COMMITTED")

        self.assertEqual(
            self.client.create_holding(
                key=self.signer2,
                identifier=self.signer1_pickles,
                label=uuid4().hex,
                description=uuid4().hex,
                asset=self.sawbucks,
                quantity=0)[0]['status'],
            "COMMITTED")

        self.assertEqual(
            self.client.create_holding(
                key=self.signer2,
                identifier=self.signer2_pickles,
                label=uuid4().hex,
                description=uuid4().hex,
                asset=self.pickles,
                quantity=10)[0]['status'],
            "COMMITTED")

    def test_03_create_offer(self):
        """Tests the CreateOffer validation rules.

        Notes:
            CreateOffer validation rules
                - No Offer already has the same id
                - The transaction signer does not have an Account.
                - The source is set.
                - The source_quantity is not 0.
                - The target or target_quantity must be both set or both unset.
                - The source is a Holding.
                - The target is a Holding.
                - The txn signer must be the account holder of both Holdings.
        """

        self.assertEqual(
            self.client.create_offer(
                key=self.signer1,
                identifier=self.sawbucks_for_pickles,
                label=uuid4().hex,
                description=uuid4().hex,
                source=self.signer1_sawbucks,
                source_quantity=1,
                target=self.signer2_sawbucks,
                target_quantity=1,
                rules=[])[0]['status'],
            "COMMITTED")

        self.assertEqual(
            self.client.create_offer(
                key=self.signer1,
                identifier=self.sawbucks_for_pickles,
                label=uuid4().hex,
                description=uuid4().hex,
                source=self.signer1_sawbucks,
                source_quantity=10,
                target=self.signer2_sawbucks,
                target_quantity=10,
                rules=[])[0]['status'],
            "INVALID",
            "The Offer id must not already exist.")

        signer_invalid = make_key()

        self.assertEqual(
            self.client.create_offer(
                key=signer_invalid,
                identifier=str(uuid4()),
                label=uuid4().hex,
                description=uuid4().hex,
                source=self.signer1_sawbucks,
                source_quantity=10,
                target=self.signer2_sawbucks,
                target_quantity=10,
                rules=[])[0]['status'],
            "INVALID",
            "The Transaction signer must have an Account")

        self.assertEqual(
            self.client.create_offer(
                key=self.signer1,
                identifier=str(uuid4()),
                label=uuid4().hex,
                description=uuid4().hex,
                source='',
                source_quantity=10,
                target=self.signer1_sawbucks,
                target_quantity=10,
                rules=[])[0]['status'],
            "INVALID",
            "The Source must be set.")

        self.assertEqual(
            self.client.create_offer(
                key=self.signer1,
                identifier=str(uuid4()),
                label=uuid4().hex,
                description=uuid4().hex,
                source=self.signer1_sawbucks,
                source_quantity=None,
                target=self.signer2_sawbucks,
                target_quantity=10,
                rules=[])[0]['status'],
            "INVALID",
            "The source quantity must be set and non-zero.")

        self.assertEqual(
            self.client.create_offer(
                key=self.signer1,
                identifier=str(uuid4()),
                label=uuid4().hex,
                description=uuid4().hex,
                source=self.signer1_sawbucks,
                source_quantity=10,
                target=self.signer2_sawbucks,
                target_quantity=None,
                rules=[])[0]['status'],
            "INVALID",
            "The target and target_quantity must be both set or unset.")

        self.assertEqual(
            self.client.create_offer(
                key=self.signer1,
                identifier=str(uuid4()),
                label=uuid4().hex,
                description=uuid4().hex,
                source=self.signer1_sawbucks,
                source_quantity=10,
                target='',
                target_quantity=10,
                rules=[])[0]['status'],
            "INVALID",
            "The target and target_quantity must be both set or unset.")

        self.assertEqual(
            self.client.create_offer(
                key=self.signer1,
                identifier=str(uuid4()),
                label=uuid4().hex,
                description=uuid4().hex,
                source=str(uuid4()),
                source_quantity=10,
                target=self.signer2_sawbucks,
                target_quantity=10,
                rules=[])[0]['status'],
            "INVALID",
            "The Source must be a Holding.")

        self.assertEqual(
            self.client.create_offer(
                key=self.signer1,
                identifier=str(uuid4()),
                label=uuid4().hex,
                description=uuid4().hex,
                source=self.signer1_sawbucks,
                source_quantity=10,
                target=str(uuid4()),
                target_quantity=10,
                rules=[])[0]['status'],
            "INVALID",
            "The target must be a Holding.")

        self.assertEqual(
            self.client.create_offer(
                key=self.signer2,
                identifier=str(uuid4()),
                label=uuid4().hex,
                description=uuid4().hex,
                source=self.signer1_sawbucks,
                source_quantity=10,
                target=self.signer2_sawbucks,
                target_quantity=11,
                rules=[])[0]['status'],
            "INVALID",
            "The txn signer must be the account holder for both source and "
            "target Holdings.")

    def test_04_accept_offer(self):
        """Tests the AcceptOffer validation rules.

        Notes
            AcceptOffer
                - The Offer exists and is Open.
                - The Source Holding has enough Quantity for the transaction.
                - The Receiver Source Holding exists and has enough
                  Quantity for the transaction.
                - The Source Holding and Receiver Target Holding are of the
                  same asset.
                - The Target Holding and Receiver Source Holding are of the
                  same asset.
        """

        offerer = transaction_creation.OfferParticipant(
            source=self.signer1_sawbucks,
            source_asset=self.sawbucks,
            target=self.signer2_sawbucks,
            target_asset=self.sawbucks)
        receiver = transaction_creation.OfferParticipant(
            source=self.signer2_pickles,
            source_asset=self.pickles,
            target=self.signer1_pickles,
            target_asset=self.pickles)

        self.assertEqual(
            self.client.accept_offer(
                key=self.signer2,
                identifier=str(uuid4()),
                receiver=receiver,
                offerer=offerer,
                count=1)[0]['status'],
            "INVALID",
            "The offer must exist")

        self.assertEqual(
            self.client.accept_offer(
                key=self.signer2,
                identifier=self.sawbucks_for_pickles,
                offerer=offerer,
                receiver=receiver,
                count=20)[0]['status'],
            "INVALID",
            "There are not enough source quantities for the AcceptOffer.")

        self.assertEqual(
            self.client.accept_offer(
                key=self.signer2,
                identifier=self.sawbucks_for_pickles,
                receiver=receiver,
                offerer=offerer,
                count=2)[0]['status'],
            "COMMITTED")

    def test_05_close_offer(self):
        """Tests the CloseOffer validation rules.

        Notes
            CloseOffer
                - The Offer exists and is Open.
                - The txn signer is a member of the Offer owners.
        """

        self.assertEqual(
            self.client.close_offer(
                self.signer2,
                str(uuid4()))[0]['status'],
            "INVALID",
            "The Offer must exist")

        self.assertEqual(
            self.client.close_offer(
                self.signer2,
                self.sawbucks_for_pickles)[0]['status'],
            "INVALID",
            "The txn signer must be an owner of the Offer.")

        self.assertEqual(
            self.client.close_offer(
                self.signer1,
                self.sawbucks_for_pickles)[0]['status'],
            "COMMITTED")

        self.assertEqual(
            self.client.close_offer(
                self.signer1,
                self.sawbucks_for_pickles)[0]['status'],
            "INVALID",
            "The Offer must be Open.")


class MarketplaceClient(object):

    def __init__(self, url):
        self._client = RestClient(base_url="http://{}".format(url))

    def create_account(self, key, label, description):
        batches, signature = transaction_creation.create_account(
            txn_key=key,
            batch_key=BATCH_KEY,
            label=label,
            description=description)
        batch_list = batch_pb2.BatchList(batches=batches)

        self._client.send_batches(batch_list)
        return self._client.get_statuses([signature], wait=10)

    def create_asset(self, key, name, description, rules):
        batches, signature = transaction_creation.create_asset(
            txn_key=key,
            batch_key=BATCH_KEY,
            name=name,
            description=description,
            rules=rules)
        batch_list = batch_pb2.BatchList(batches=batches)
        self._client.send_batches(batch_list)
        return self._client.get_statuses([signature], wait=10)

    def create_holding(self,
                       key,
                       identifier,
                       label,
                       description,
                       asset,
                       quantity):
        batches, signature = transaction_creation.create_holding(
            txn_key=key,
            batch_key=BATCH_KEY,
            identifier=identifier,
            label=label,
            description=description,
            asset=asset,
            quantity=quantity)
        batch_list = batch_pb2.BatchList(batches=batches)
        self._client.send_batches(batch_list)
        return self._client.get_statuses([signature], wait=10)

    def create_offer(self,
                     key,
                     identifier,
                     label,
                     description,
                     source,
                     source_quantity,
                     target,
                     target_quantity,
                     rules):
        batches, signature = transaction_creation.create_offer(
            txn_key=key,
            batch_key=BATCH_KEY,
            identifier=identifier,
            label=label,
            description=description,
            source=source,
            source_quantity=source_quantity,
            target=target,
            target_quantity=target_quantity,
            rules=rules)
        batch_list = batch_pb2.BatchList(batches=batches)
        self._client.send_batches(batch_list)
        return self._client.get_statuses([signature], wait=10)

    def accept_offer(self,
                     key,
                     identifier,
                     receiver,
                     offerer,
                     count):
        batches, signature = transaction_creation.accept_offer(
            txn_key=key,
            batch_key=BATCH_KEY,
            identifier=identifier,
            offerer=offerer,
            receiver=receiver,
            count=count)
        batch_list = batch_pb2.BatchList(batches=batches)
        self._client.send_batches(batch_list)
        return self._client.get_statuses([signature], wait=10)

    def close_offer(self,
                    key,
                    identifier):
        batches, signature = transaction_creation.close_offer(
            txn_key=key,
            batch_key=BATCH_KEY,
            identifier=identifier)

        batch_list = batch_pb2.BatchList(batches=batches)
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
