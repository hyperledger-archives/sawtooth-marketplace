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

from marketplace_processor.protobuf import offer_pb2


def handle_close_offer(close_offer, header, state):
    """Handle Offer closure.

    Args:
        close_offer (CloseOffer): The transaction.
        header (TransactionHeader): The TransactionHeader.
        state (MarketplaceState): The wrapper around the context.

    Raises:
        - InvalidTransaction
            - The Offer doesn't exist.
            - The txn signer is not within the owners of the Offer.
    """

    offer = state.get_offer(close_offer.id)

    if not offer:
        raise InvalidTransaction(
            "Failed to close offer, the offer id {} "
            "does not reference an Offer.".format(
                close_offer.id))

    if not offer.status == offer_pb2.Offer.OPEN:
        raise InvalidTransaction(
            "Failed to close offer, the Offer {} is {} "
            "not open".format(offer.id, offer.status))

    if header.signer_public_key not in offer.owners:
        raise InvalidTransaction(
            "Failed to close offer, the txn signer {} "
            "is not a member of the offer's owners.".format(
                header.signer_public_key))

    state.close_offer(close_offer.id)
