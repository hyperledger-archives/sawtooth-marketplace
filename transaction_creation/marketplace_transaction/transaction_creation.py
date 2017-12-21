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

from marketplace_addressing import addresser

from marketplace_transaction.common import make_header_and_batch
from marketplace_transaction.protobuf import payload_pb2


def create_account(txn_key, batch_key, label, description):
    """Create a CreateAccount txn and wrap it in a batch and list.

    Args:
        txn_key (sawtooth_signing.Signer): The Txn signer key pair.
        batch_key (sawtooth_signing.Signer): The Batch signer key pair.
        label (str): The account's label.
        description (str): The description of the account.

    Returns:
        tuple: List of Batch, signature tuple
    """

    inputs = [addresser.make_account_address(
        account_id=txn_key.get_public_key().as_hex())]

    outputs = [addresser.make_account_address(
        account_id=txn_key.get_public_key().as_hex())]

    account = payload_pb2.CreateAccount(
        label=label,
        description=description)
    payload = payload_pb2.TransactionPayload(
        payload_type=payload_pb2.TransactionPayload.CREATE_ACCOUNT,
        create_account=account)

    return make_header_and_batch(
        payload=payload,
        inputs=inputs,
        outputs=outputs,
        txn_key=txn_key,
        batch_key=batch_key)


def create_asset(txn_key, batch_key, name, description, rules):
    """Create a CreateAsset txn and wrap it in a batch and list.

    Args:
        txn_key (sawtooth_signing.Signer): The txn signer key pair.
        batch_key (sawtooth_signing.Signer): The batch signer key pair.
        name (str): The name of the asset.
        description (str): A description of the asset.
        rules (list): List of protobuf.rule_pb2.Rule

    Returns:
        tuple: List of Batch, signature tuple
    """

    inputs = [addresser.make_asset_address(asset_id=name),
              addresser.make_account_address(
                  account_id=txn_key.get_public_key().as_hex())]

    outputs = [addresser.make_asset_address(asset_id=name)]

    asset = payload_pb2.CreateAsset(
        name=name,
        description=description,
        rules=rules
    )

    payload = payload_pb2.TransactionPayload(
        payload_type=payload_pb2.TransactionPayload.CREATE_ASSET,
        create_asset=asset)

    return make_header_and_batch(
        payload=payload,
        inputs=inputs,
        outputs=outputs,
        txn_key=txn_key,
        batch_key=batch_key)


def create_holding(txn_key,
                   batch_key,
                   identifier,
                   label,
                   description,
                   asset,
                   quantity):
    """Create a CreateHolding txn and wrap it in a batch and list.

    Args:
        txn_key (sawtooth_signing.Signer): The txn signer key pair.
        batch_key (sawtooth_signing.Signer): The batch signer key pair.
        identifier (str): The identifier of the Holding.
        label (str): The label of the Holding.
        description (str): The description of the Holding.
        quantity (int): The amount of the Asset.

    Returns:
        tuple: List of Batch, signature tuple
    """

    inputs = [
        addresser.make_account_address(
            account_id=txn_key.get_public_key().as_hex()),
        addresser.make_asset_address(asset_id=asset),
        addresser.make_holding_address(holding_id=identifier)
    ]

    outputs = [addresser.make_holding_address(holding_id=identifier),
               addresser.make_account_address(
                   account_id=txn_key.get_public_key().as_hex())]

    holding_txn = payload_pb2.CreateHolding(
        id=identifier,
        label=label,
        description=description,
        asset=asset,
        quantity=quantity)

    payload = payload_pb2.TransactionPayload(
        payload_type=payload_pb2.TransactionPayload.CREATE_HOLDING,
        create_holding=holding_txn)

    return make_header_and_batch(
        payload=payload,
        inputs=inputs,
        outputs=outputs,
        txn_key=txn_key,
        batch_key=batch_key)


def create_offer(txn_key,
                 batch_key,
                 identifier,
                 label,
                 description,
                 source,
                 target,
                 rules):
    """Create a CreateOffer txn and wrap it in a batch and list.

    Args:
        txn_key (sawtooth_signing.Signer): The Txn signer key pair.
        batch_key (sawtooth_signing.Signer): The Batch signer key pair.
        identifier (str): The identifier of the Offer.
        label (str): The offer's label.
        description (str): The description of the offer.
        source (MarketplaceHolding): The holding id, quantity, asset to be
            drawn from.
        target (MarketplaceHolding): The holding id, quantity, asset to be
            paid into.
        rules (list): List of protobuf.rule_pb2.Rule


    Returns:
        tuple: List of Batch, signature tuple
    """

    inputs = [
        addresser.make_account_address(
            account_id=txn_key.get_public_key().as_hex()),
        addresser.make_holding_address(
            holding_id=source.holding_id),
        addresser.make_offer_address(offer_id=identifier),
        addresser.make_asset_address(asset_id=source.asset)
    ]
    if target.holding_id:
        inputs.append(addresser.make_holding_address(
            holding_id=target.holding_id))
        inputs.append(addresser.make_asset_address(target.asset))

    outputs = [addresser.make_offer_address(offer_id=identifier)]

    offer_txn = payload_pb2.CreateOffer(
        id=identifier,
        label=label,
        description=description,
        source=source.holding_id,
        source_quantity=source.quantity,
        target=target.holding_id,
        target_quantity=target.quantity,
        rules=rules)

    payload = payload_pb2.TransactionPayload(
        payload_type=payload_pb2.TransactionPayload.CREATE_OFFER,
        create_offer=offer_txn)

    return make_header_and_batch(
        payload=payload,
        inputs=inputs,
        outputs=outputs,
        txn_key=txn_key,
        batch_key=batch_key)


def accept_offer(txn_key,
                 batch_key,
                 identifier,
                 offerer,
                 receiver,
                 count):
    """Create an AcceptOffer txn and wrap it in a Batch and list.

    Args:
        txn_key (sawtooth_signing.Signer): The Txn signer key pair.
        batch_key (sawtooth_signing.Signer): The Batch signer key pair.
        identifier (str): The identifier of the Offer.
        offerer (OfferParticipant): The participant who made the offer.
        receiver (OfferParticipant): The participant who is accepting
            the offer.
        count (int): The number of units of exchange.

    Returns:
        tuple: List of Batch, signature tuple
    """

    inputs = [addresser.make_holding_address(receiver.target),
              addresser.make_holding_address(offerer.source),
              addresser.make_asset_address(receiver.target_asset),
              addresser.make_asset_address(offerer.source_asset),
              addresser.make_offer_history_address(offer_id=identifier),
              addresser.make_offer_account_address(
                  offer_id=identifier,
                  account=txn_key.get_public_key().as_hex()),
              addresser.make_offer_address(identifier)]

    outputs = [addresser.make_holding_address(receiver.target),
               addresser.make_holding_address(offerer.source),
               addresser.make_offer_history_address(offer_id=identifier),
               addresser.make_offer_account_address(
                   offer_id=identifier,
                   account=txn_key.get_public_key().as_hex())]

    if receiver.source is not None:
        inputs.append(addresser.make_holding_address(receiver.source))
        inputs.append(addresser.make_asset_address(receiver.source_asset))
        outputs.append(addresser.make_holding_address(receiver.source))

    if offerer.target is not None:
        inputs.append(addresser.make_holding_address(offerer.target))
        inputs.append(addresser.make_asset_address(offerer.target_asset))
        outputs.append(addresser.make_holding_address(offerer.target))

    accept_txn = payload_pb2.AcceptOffer(
        id=identifier,
        source=receiver.source,
        target=receiver.target,
        count=count)

    payload = payload_pb2.TransactionPayload(
        payload_type=payload_pb2.TransactionPayload.ACCEPT_OFFER,
        accept_offer=accept_txn)

    return make_header_and_batch(
        payload=payload,
        inputs=inputs,
        outputs=outputs,
        txn_key=txn_key,
        batch_key=batch_key)


def close_offer(txn_key, batch_key, identifier):
    """Create a CloseOffer txn and wrap it in a Batch and list.

    Args:
        txn_key (sawtooth_signing.Signer): The Txn signer key pair.
        batch_key (sawtooth_signing.Signer): The Batch signer key pair.
        identifier (str): The Offer identifier.

    Returns:
        tuple: List of Batch, signature tuple
    """

    inputs = [addresser.make_offer_address(identifier)]

    outputs = [addresser.make_offer_address(identifier)]

    close_txn = payload_pb2.CloseOffer(id=identifier)

    payload = payload_pb2.TransactionPayload(
        payload_type=payload_pb2.TransactionPayload.CLOSE_OFFER,
        close_offer=close_txn)

    return make_header_and_batch(
        payload=payload,
        inputs=inputs,
        outputs=outputs,
        txn_key=txn_key,
        batch_key=batch_key)


class OfferParticipant(object):

    def __init__(self, source, target, source_asset, target_asset):
        """Constructor

        Args:
            source (str): The id of the source Holding.
            target (str): The id of the target Holding.
            source_asset (str): The id of the source Asset.
            target_asset (str): The id of the target Asset.
        """

        self._source = source
        self._source_asset = source_asset

        self._target = target
        self._target_asset = target_asset

    @property
    def source(self):
        return self._source

    @property
    def source_asset(self):
        return self._source_asset

    @property
    def target(self):
        return self._target

    @property
    def target_asset(self):
        return self._target_asset


class MarketplaceHolding(object):

    def __init__(self, holding_id, quantity, asset):
        self._holding_id = holding_id
        self._quantity = quantity
        self._asset = asset

    @property
    def holding_id(self):
        return self._holding_id

    @property
    def quantity(self):
        return self._quantity

    @property
    def asset(self):
        return self._asset
