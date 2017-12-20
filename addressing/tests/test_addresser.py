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

import unittest
from uuid import uuid4

from marketplace_addressing import addresser


class AddresserTest(unittest.TestCase):

    def test_asset_address(self):

        asset_address = addresser.make_asset_address(uuid4().hex)

        self.assertEqual(len(asset_address), 70, "The address is valid.")

        self.assertEqual(addresser.address_is(asset_address),
                         addresser.AddressSpace.ASSET,
                         "The address is correctly identified as an Asset.")

    def test_offer_address(self):
        offer_address = addresser.make_offer_address(uuid4().hex)

        self.assertEqual(len(offer_address), 70, "The address is valid.")

        self.assertEqual(addresser.address_is(offer_address),
                         addresser.AddressSpace.OFFER,
                         "The address is correctly identified as an Offer.")

    def test_account_address(self):
        account_address = addresser.make_account_address(uuid4().hex)

        self.assertEqual(len(account_address), 70, "The address is valid.")

        self.assertEqual(addresser.address_is(account_address),
                         addresser.AddressSpace.ACCOUNT,
                         "The address is correctly identified as an Account.")

    def test_holding_address(self):
        holding_address = addresser.make_holding_address(uuid4().hex)

        self.assertEqual(len(holding_address), 70, "The address is valid.")

        self.assertEqual(addresser.address_is(holding_address),
                         addresser.AddressSpace.HOLDING,
                         "The address is correctly identified as an Holding.")

    def test_offer_history_address(self):
        offer_history_address = addresser.make_offer_account_address(
            uuid4().hex,
            uuid4().hex)

        self.assertEqual(len(offer_history_address), 70, "The address is valid")
