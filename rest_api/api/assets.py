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

from urllib.parse import unquote

from sanic import Blueprint
from sanic import response

from api.authorization import authorized
from api import common
from api import messaging

from db import assets_query

from marketplace_transaction import transaction_creation


ASSETS_BP = Blueprint('assets')


@ASSETS_BP.post('assets')
@authorized()
async def create_asset(request):
    """Creates a new Asset in state"""
    required_fields = ['name']
    common.validate_fields(required_fields, request.json)

    signer = await common.get_signer(request)
    asset = _create_asset_dict(request.json, signer.get_public_key().as_hex())

    batches, batch_id = transaction_creation.create_asset(
        txn_key=signer,
        batch_key=request.app.config.SIGNER,
        name=asset.get('name'),
        description=asset.get('description'),
        rules=asset.get('rules'))

    await messaging.send(
        request.app.config.VAL_CONN,
        request.app.config.TIMEOUT,
        batches)

    await messaging.check_batch_status(request.app.config.VAL_CONN, batch_id)

    if asset.get('rules'):
        asset['rules'] = request.json['rules']

    return response.json(asset)


@ASSETS_BP.get('assets')
async def get_all_assets(request):
    """Fetches complete details of all Assets in state"""
    asset_resources = await assets_query.fetch_all_asset_resources(
        request.app.config.DB_CONN)
    return response.json(asset_resources)


@ASSETS_BP.get('assets/<name>')
async def get_asset(request, name):
    """Fetches the details of particular Asset in state"""
    decoded_name = unquote(name)
    asset_resource = await assets_query.fetch_asset_resource(
        request.app.config.DB_CONN, decoded_name)
    return response.json(asset_resource)


def _create_asset_dict(body, public_key):
    keys = ['name', 'description']

    asset = {k: body[k] for k in keys if body.get(k) is not None}
    asset['owners'] = [public_key]

    if body.get('rules'):
        asset['rules'] = common.proto_wrap_rules(body['rules'])

    return asset
