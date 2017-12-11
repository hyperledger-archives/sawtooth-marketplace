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
from sanic.response import json

from api.authorization import authorized
from api import common
from api import messaging
from api.errors import ApiBadRequest

from db import assets_query

from marketplace_transaction import transaction_creation
from marketplace_transaction.protobuf import rule_pb2


ASSETS_BP = Blueprint('assets')


@ASSETS_BP.post('assets')
@authorized()
async def create_asset(request):
    """Creates a new Asset in state"""
    required_fields = ['name']
    common.validate_fields(required_fields, request.json)
    signer = await common.get_signer(request)
    batches, batch_id = transaction_creation.create_asset(
        signer,
        request.app.config.SIGNER,
        request.json.get('name'),
        request.json.get('description'),
        _proto_wrap_rules(request.json.get('rules')))
    await messaging.send(
        request.app.config.VAL_CONN,
        request.app.config.TIMEOUT,
        batches)
    await messaging.check_batch_status(request.app.config.VAL_CONN, batch_id)
    return _create_asset_response(request, signer.get_public_key().as_hex())


@ASSETS_BP.get('assets')
async def get_all_assets(request):
    """Fetches complete details of all Assets in state"""
    asset_resources = await assets_query.fetch_all_asset_resources(
        request.app.config.DB_CONN)
    return json(asset_resources)


@ASSETS_BP.get('assets/<name>')
async def get_asset(request, name):
    """Fetches the details of particular Asset in state"""
    decoded_name = unquote(name)
    asset_resource = await assets_query.fetch_asset_resource(
        request.app.config.DB_CONN, decoded_name)
    return json(asset_resource)


def _proto_wrap_rules(rules):
    rule_protos = []
    if rules is not None:
        for rule in rules:
            try:
                rule_proto = rule_pb2.Rule(type=rule['type'])
                rule_protos.append(rule_proto)
            except IndexError:
                raise ApiBadRequest("Bad Request: Improper rule format")
            except ValueError:
                raise ApiBadRequest("Bad Request: Invalid rule type")
    return rule_protos


def _create_asset_response(request, public_key):
    asset_resource = {
        'name': request.json.get('name'),
        'owners': [public_key]
    }
    if request.json.get('description'):
        asset_resource['description'] = request.json.get('description')
    if request.json.get('rules'):
        asset_resource['rules'] = request.json.get('rules')
    return json(asset_resource)
