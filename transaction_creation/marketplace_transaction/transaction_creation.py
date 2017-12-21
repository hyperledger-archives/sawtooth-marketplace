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
        account (str): The account's public key.
        holding (str): The asset's identifier.
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


def create_offer(txn_key, batch_key, identifier, label, description,
                 source, source_quantity, target, target_quantity, rules):
    """Create a CreateOffer txn and wrap it in a batch and list.

    Args:
        txn_key (sawtooth_signing.Signer): The Txn signer key pair.
        batch_key (sawtooth_signing.Signer): The Batch signer key pair.
        identifier (str): The identifier of the Offer.
        label (str): The offer's label.
        description (str): The description of the offer.
        source (str): The id of a Holding from which resources will be drawn.
        source_quantity (int): The quantity of resources to send.
        target (str): The id of a Holding which will receive resources.
        target_quantity (int): The quantity of resources to require.
        rules (list): List of protobuf.rule_pb2.Rule


    Returns:
        tuple: List of Batch, signature tuple
    """

    inputs = [
        addresser.make_account_address(
            account_id=txn_key.get_public_key().as_hex()),
        addresser.make_holding_address(holding_id=source),
        addresser.make_offer_address(offer_id=identifier)
    ]
    if target is not None:
        inputs.append(addresser.make_holding_address(holding_id=target))

    outputs = [addresser.make_offer_address(offer_id=identifier)]

    offer_txn = payload_pb2.CreateOffer(
        id=identifier,
        label=label,
        description=description,
        source=source,
        source_quantity=source_quantity,
        target=target,
        target_quantity=target_quantity,
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
                 receiver_source,
                 offerer_source,
                 receiver_target,
                 offerer_target,
                 count):
    """Create an AcceptOffer txn and wrap it in a Batch and list.

    Args:
        txn_key (sawtooth_signing.Signer): The Txn signer key pair.
        batch_key (sawtooth_signing.Signer): The Batch signer key pair.
        identifier (str): The identifier of the Offer.
        receiver_source (str): The Holding that the receiver gives up.
            Must be the same Asset as offerer_target.
        offerer_source (str): The Holding that the Offerer gives up.
        receiver_target (str): The Holding that the receiver receives.
            Must be the same Asset as the offerer_source.
        offerer_target (str): The Holding that the offerer receives.
        count (int): The number of units of exchange.

    Returns:
        tuple: List of Batch, signature tuple
    """

    inputs = [addresser.make_holding_address(receiver_target),
              addresser.make_holding_address(offerer_source),
              addresser.make_offer_address(identifier)]

    outputs = [addresser.make_holding_address(receiver_target),
               addresser.make_holding_address(offerer_source)]

    if receiver_source is not None:
        inputs.append(addresser.make_holding_address(receiver_source))
        outputs.append(addresser.make_holding_address(receiver_source))

    if offerer_target is not None:
        inputs.append(addresser.make_holding_address(offerer_target))
        outputs.append(addresser.make_holding_address(offerer_target))

    accept_txn = payload_pb2.AcceptOffer(
        id=identifier,
        source=receiver_source,
        target=receiver_target,
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
