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

from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.handler import TransactionHandler

from marketplace_addressing import addresser

from marketplace_processor.account import account_creation
from marketplace_processor.asset import asset_creation
from marketplace_processor.holding import holding_creation
from marketplace_processor.offer import offer_acceptance
from marketplace_processor.offer import offer_closure
from marketplace_processor.offer import offer_creation
from marketplace_processor.marketplace_payload import MarketplacePayload
from marketplace_processor.marketplace_state import MarketplaceState


class MarketplaceHandler(TransactionHandler):

    @property
    def family_name(self):
        return addresser.FAMILY_NAME

    @property
    def namespaces(self):
        return [addresser.NS]

    @property
    def family_versions(self):
        return ['1.0']

    def apply(self, transaction, context):

        state = MarketplaceState(context=context, timeout=2)
        payload = MarketplacePayload(payload=transaction.payload)

        if payload.is_create_account():
            account_creation.handle_account_creation(
                payload.create_account(),
                header=transaction.header,
                state=state)
        elif payload.is_create_asset():
            asset_creation.handle_asset_creation(
                payload.create_asset(),
                header=transaction.header,
                state=state)
        elif payload.is_create_holding():
            holding_creation.handle_holding_creation(
                payload.create_holding(),
                header=transaction.header,
                state=state)
        elif payload.is_create_offer():
            offer_creation.handle_offer_creation(
                payload.create_offer(),
                header=transaction.header,
                state=state)
        elif payload.is_accept_offer():
            offer_acceptance.handle_accept_offer(
                payload.accept_offer(),
                header=transaction.header,
                state=state)
        elif payload.is_close_offer():
            offer_closure.handle_close_offer(
                payload.close_offer(),
                header=transaction.header,
                state=state)

        else:
            raise InvalidTransaction("Transaction payload type unknown.")
