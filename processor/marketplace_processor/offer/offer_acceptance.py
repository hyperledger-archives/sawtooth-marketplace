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

from marketplace_processor.offer.accept_calc import AcceptOfferCalculator
from marketplace_processor.protobuf import offer_pb2


def handle_accept_offer(accept_offer, header, state):
    """Handle Offer acceptance.

    Args:
        accept_offer (AcceptOffer): The transaction.
        header (TransactionHeader): The TransactionHeader.
        state (MarketplaceState): The wrapper around the context.

    Raises:
        - InvalidTransaction
            - The Offer does not exist or is not Open
            - The receiver source Holding does not exist.
            - The receiver target Holding does not exist.
            - The offerer source holding asset does not match the
              receiver target holding asset.
            - The offerer target holding asset does not match the
              the receiver source holding asset.
            - The receiver source holding does not have the required quantity.
            - The offerer source holding does not have the required quantity.
    """

    offer = state.get_offer(identifier=accept_offer.id)

    check_validity_of_offer(offer, accept_offer)

    offer_accept = OfferAcceptance(offer, accept_offer, state)

    # The holding ids referernce Holdings.
    offer_accept.validate_output_holding_exists()

    offer_accept.validate_input_holding_exists()

    # The assets match for the Holdings
    offer_accept.validate_input_holding_assets()

    offer_accept.validate_output_holding_assets()

    calculator = AcceptOfferCalculator(offer=offer, count=accept_offer.count)

    # There is enough in each Holding to make the transaction.
    offer_accept.validate_output_enough(calculator.output_quantity())

    offer_accept.validate_input_enough(calculator.input_quantity())

    # Handle incrementing and decrementing the Holdings' quantity
    offer_accept.handle_offerer_source(calculator.input_quantity())
    offer_accept.handle_offerer_target(calculator.output_quantity())
    offer_accept.handle_receiver_source(calculator.output_quantity())
    offer_accept.handle_receiver_target(calculator.input_quantity())


def check_validity_of_offer(offer, accept_offer):
    """Checks that the offer exists and is open.

    Args:
        offer (offer_pb2.Offer): The offer.
        accept_offer (AcceptOffer): The AcceptOffer txn.

    Raises:
        - InvalidTransaction
    """

    if not offer:
        raise InvalidTransaction(
            "Failed to accept Offer, Offer {} does not exist".format(
                accept_offer.id))
    if not offer.status == offer_pb2.Offer.OPEN:
        raise InvalidTransaction(
            "Failed to accept Offer, Offer {} is not open".format(
                accept_offer.id))


class OfferAcceptance(object):

    def __init__(self, offer, accept_offer, state):
        self._offer = offer
        self._accept_offer = accept_offer

        self._state = state

        self._off_source_hldng = state.get_holding(offer.source)

        self._off_target_hldng = state.get_holding(offer.target) \
            if offer.target else None

        self._rec_source_hldng = state.get_holding(accept_offer.source) \
            if accept_offer.source else None

        self._rec_target_hldng = state.get_holding(accept_offer.target)

    def validate_output_holding_exists(self):
        if self._offer.target and self._accept_offer.source:
            if self._off_target_hldng and not self._rec_source_hldng:
                raise InvalidTransaction(
                    "Failed to accept offer, holding specified as source,{},"
                    " does not exist.".format(self._accept_offer.source))

    def validate_input_holding_exists(self):
        if not self._rec_target_hldng:
            raise InvalidTransaction(
                "Failed to accept offer, holding specified as target, {},"
                " does not exist".format(self._accept_offer.target))

    def validate_input_holding_assets(self):
        if not self._off_source_hldng.asset == self._rec_target_hldng.asset:
            raise InvalidTransaction(
                "Failed to accept offer, expected Holding asset {}, got "
                "asset {}".format(self._off_source_hldng.asset,
                                  self._rec_target_hldng.asset))

    def validate_output_holding_assets(self):
        if self._offer.target \
                and self._off_target_hldng \
                and not \
                self._off_target_hldng.asset == self._rec_source_hldng.asset:
            raise InvalidTransaction(
                "Failed to accept offer, expected Holding asset {}, got "
                "asset {}.".format(self._off_target_hldng.asset,
                                   self._rec_source_hldng.asset))

    def validate_output_enough(self, output_quantity):
        if self._accept_offer.source and \
                output_quantity > self._rec_source_hldng.quantity:
            raise InvalidTransaction(
                "Failed to accept offer, needed quantity {}, but only had {} "
                "of {}".format(output_quantity,
                               self._rec_source_hldng.quantity,
                               self._rec_source_hldng.asset))

    def validate_input_enough(self, input_quantity):
        if input_quantity > self._off_source_hldng.quantity:
            raise InvalidTransaction(
                "Failed to accept offer, needed quantity {}, but only had {} "
                "of {}".format(input_quantity,
                               self._off_source_hldng.quantity,
                               self._off_source_hldng.asset))

    def handle_offerer_source(self, input_quantity):
        self._state.change_holding_quantity(
            self._off_source_hldng.id,
            self._off_source_hldng.quantity - input_quantity)

    def handle_offerer_target(self, output_quantity):
        if self._offer.target:
            self._state.change_holding_quantity(
                self._off_target_hldng.id,
                self._off_target_hldng.quantity + output_quantity)

    def handle_receiver_source(self, output_quantity):
        if self._accept_offer.source:
            self._state.change_holding_quantity(
                self._rec_source_hldng.id,
                self._rec_source_hldng.quantity - output_quantity)

    def handle_receiver_target(self, input_quantity):
        self._state.change_holding_quantity(
            self._rec_target_hldng.id,
            self._rec_target_hldng.quantity + input_quantity)
