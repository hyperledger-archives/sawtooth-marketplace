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
    """Create a CreateAccount txn and wrap it in a batch and batchlist.

    Args:
        txn_key (sawtooth_signing.Signer): The Txn signer key pair.
        batch_key (sawtooth_signing.Signer): The Batch signer key pair.
        label (str): The account's label.
        description (str): The description of the account.

    Returns:
        tuple: BatchList, signature tuple
    """

    inputs = [addresser.make_account_address(
        account_id=txn_key.get_public_key().as_hex())]

    outputs = [addresser.make_account_address(
        account_id=txn_key.get_public_key().as_hex())]

    account = payload_pb2.CreateAccount(
        label=label,
        description=description)
    payload = payload_pb2.TransactionPayload(create_account=account)

    return make_header_and_batch(
        payload=payload,
        inputs=inputs,
        outputs=outputs,
        txn_key=txn_key,
        batch_key=batch_key)
