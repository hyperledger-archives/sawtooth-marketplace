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


def handle_holding_creation(create_holding, header, state):
    """

    Args:
        create_holding (CreateHolding): The transaction.
        header (TransactionHeader): The header of the Transaction.
        state (MarketplaceState): The wrapper around the context.

    Raises:
        InvalidTransaction
            - There is already a Holding with the same identifier.
            - The txn signer does not own an Account.
            - The Asset does not exist.
            - The quantity is not 0 and the Asset owner doesn't match the
              transaction signer public key.
    """

    if state.get_holding(identifier=create_holding.id):
        raise InvalidTransaction("Failed to create Holding, id {} already "
                                 "exists.".format(create_holding.id))

    if not state.get_account(public_key=header.signer_public_key):
        raise InvalidTransaction(
            "Failed to create Holding, account {} does not exist.".format(
                header.signer_public_key))

    asset = state.get_asset(name=create_holding.asset)
    if not asset:
        raise InvalidTransaction(
            "Failed to create Holding, asset {} does not "
            "exist.".format(create_holding.asset))

    if create_holding.quantity > 0 and \
            header.signer_public_key not in asset.owners:
        raise InvalidTransaction(
            "Failed to create Holding, quantity {} is non-zero and the "
            "transaction signer public key {} is not an owner of "
            "the Asset {}".format(create_holding.quantity,
                                  header.signer_public_key,
                                  asset.name))

    state.set_holding(
        identifier=create_holding.id,
        label=create_holding.label,
        description=create_holding.description,
        account=header.signer_public_key,
        asset=create_holding.asset,
        quantity=create_holding.quantity)

    state.add_holding_to_account(
        public_key=header.signer_public_key,
        holding_id=create_holding.id)
