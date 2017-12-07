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


def handle_asset_creation(create_asset, header, state):
    """Handles creating an Asset.

    Args:
        create_asset (CreateAsset): The transaction.
        header (TransactionHeader): The header of the Transaction.
        state (MarketplaceState): The wrapper around the context.

    Raises:
        InvalidTransaction
            - The name already exists for an Asset.
            - The txn signer has an account
    """

    if not state.get_account(public_key=header.signer_public_key):
        raise InvalidTransaction(
            "Unable to create asset, signing key has no"
            " Account: {}".format(header.signer_public_key))

    if state.get_asset(name=create_asset.name):
        raise InvalidTransaction(
            "Asset already exists with Name {}".format(create_asset.name))

    state.set_asset(
        name=create_asset.name,
        description=create_asset.description,
        owners=[header.signer_public_key],
        rules=create_asset.rules)
