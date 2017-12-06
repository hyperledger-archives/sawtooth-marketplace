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
# ------------------------------------------------------------------------------

import bcrypt

from sanic import Blueprint
from sanic.response import json

from sawtooth_signing import CryptoFactory

from api import common
from api import messaging
from api.errors import ApiBadRequest
from api.errors import ApiNotImplemented
from api.errors import ApiInternalError

from db import auth_query

from marketplace_transaction import transaction_creation


ACCOUNTS_BP = Blueprint('accounts')


@ACCOUNTS_BP.post('accounts')
async def create_account(request):
    """Creates a new Account and corresponding authorization token"""
    required_fields = ['email', 'password']
    common.validate_fields(required_fields, request.json)
    private_key = request.app.config.CONTEXT.new_random_private_key()
    signer = CryptoFactory(request.app.config.CONTEXT).new_signer(private_key)
    public_key = signer.get_public_key().as_hex()
    encrypted_private_key = common.encrypt_private_key(
        request.app.config.AES_KEY, public_key, private_key.as_hex())
    hashed_password = bcrypt.hashpw(
        bytes(request.json.get('password'), 'utf-8'), bcrypt.gensalt())
    auth_entry = {
        'public_key': public_key,
        'hashed_password': hashed_password,
        'encrypted_private_key': encrypted_private_key,
        'email': request.json.get('email')
    }
    await auth_query.create_auth_entry(request.app.config.DB_CONN, auth_entry)
    batches, _ = transaction_creation.create_account(
        signer,
        request.app.config.SIGNER,
        request.json.get('label'),
        request.json.get('description'))
    try:
        await messaging.send(
            request.app.config.VAL_CONN,
            request.app.config.TIMEOUT,
            batches)
    except (ApiBadRequest, ApiInternalError) as err:
        await auth_query.remove_auth_entry(
            request.app.config.DB_CONN, request.json.get('email'))
        raise err
    return _create_account_response(request, public_key)


@ACCOUNTS_BP.get('accounts')
async def get_all_accounts(request):
    """Fetches complete details of all Accounts in state"""
    raise ApiNotImplemented()


@ACCOUNTS_BP.get('accounts/<account_id>')
async def get_account(request, account_id):
    """Fetches the details of particular Account in state"""
    raise ApiNotImplemented()


def _create_account_response(request, public_key):
    token = common.generate_auth_token(
        request.app.config.SECRET_KEY,
        request.json.get('email'))
    account_resource = {
        'public_key': public_key,
        'holdings': [],
        'email': request.json.get('email')
    }
    if request.json.get('label'):
        account_resource['label'] = request.json.get('label')
    if request.json.get('description'):
        account_resource['description'] = request.json.get('description')
    return json(
        {
            'authorization': token,
            'account': account_resource
        })
