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

from marketplace_processor.protobuf import payload_pb2


class MarketplacePayload(object):

    def __init__(self, payload):
        self._transaction = payload_pb2.TransactionPayload()
        self._transaction.ParseFromString(payload)

    def create_account(self):
        """Returns the value set in the create_account.

        Used for both checking that the CreateAccount transaction exists
        and returning that txn.

        Returns:
            payload_pb2.CreateAccount
        """

        return self._transaction.create_account

    def create_holding(self):
        """Returns the value set in the create_holding.

        Used for both checking that the CreateHolding transaction exists
        and returning the txn.

        Returns:
            payload_pb2.CreateHolding
        """

        return self._transaction.create_holding

    def create_asset(self):
        """Returns the value set in the create_asset.

        Returns:
            payload_pb2.CreateAsset
        """

        return self._transaction.create_asset

    def create_offer(self):
        """Returns the value set in the create_offer.

        Returns:
            payload_pb2.CreateOffer
        """

        return self._transaction.create_offer

    def accept_offer(self):
        """Returns the value set in accept_offer.

        Returns:
            payload_pb2.AcceptOffer
        """

        return self._transaction.accept_offer

    def close_offer(self):
        """Returns the value set in close_offer.

        Returns:
            payload_pb2.CloseOffer
        """

        return self._transaction.close_offer
