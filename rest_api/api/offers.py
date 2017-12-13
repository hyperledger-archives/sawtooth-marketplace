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

from uuid import uuid4

from sanic import response
from sanic import Blueprint

from api.authorization import authorized
from api import common
from api import messaging
from api.errors import ApiBadRequest
from api.errors import ApiNotImplemented

from db import offers_query

from marketplace_transaction import transaction_creation


OFFERS_BP = Blueprint('offers')


@OFFERS_BP.post('offers')
@authorized()
async def create_offer(request):
    """Creates a new Offer in state"""
    required_fields = ['source', 'sourceQuantity']
    common.validate_fields(required_fields, request.json)

    signer = await common.get_signer(request)
    offer = _create_offer_dict(request.json, signer.get_public_key().as_hex())

    batches, batch_id = transaction_creation.create_offer(
        txn_key=signer,
        batch_key=request.app.config.SIGNER,
        identifier=offer['id'],
        label=offer.get('label'),
        description=offer.get('description'),
        source=offer['source'],
        source_quantity=offer['sourceQuantity'],
        target=offer.get('target'),
        target_quantity=offer.get('targetQuantity'),
        rules=common.proto_wrap_rules(offer.get('rules')))

    await messaging.send(
        request.app.config.VAL_CONN,
        request.app.config.TIMEOUT,
        batches)

    await messaging.check_batch_status(request.app.config.VAL_CONN, batch_id)

    return response.json(offer)


@OFFERS_BP.get('offers')
async def get_all_offers(request):
    """Fetches complete details of all Offers in state"""
    keys = ['status', 'source', 'target']
    query_params = {
        k: request.args[k][0] for k in keys if request.args.get(k) is not None
    }
    offer_resources = await offers_query.fetch_all_offer_resources(
        request.app.config.DB_CONN, query_params)
    return response.json(offer_resources)


@OFFERS_BP.get('offers/<offer_id>')
async def get_offer(request, offer_id):
    """Fetches the details of particular Offer in state"""
    offer_resource = await offers_query.fetch_offer_resource(
        request.app.config.DB_CONN, offer_id)
    return response.json(offer_resource)


@OFFERS_BP.patch('offers/<offer_id>/accept')
@authorized()
async def accept_offer(request, offer_id):
    """Request for authorized Account to accept Offer"""
    raise ApiNotImplemented()


@OFFERS_BP.patch('offers/<offer_id>/close')
@authorized()
async def close_offer(request, offer_id):
    """Request by owner of Offer to close it"""
    raise ApiNotImplemented()


def _create_offer_dict(body, public_key):
    keys = ['label', 'description', 'source', 'rules',
            'sourceQuantity', 'target', 'targetQuantity']

    offer = {k: body[k] for k in keys if body.get(k) is not None}

    if offer['sourceQuantity'] < 1:
        raise ApiBadRequest("sourceQuantity must be a positive integer")
    if offer.get('targetQuantity') and offer['targetQuantity'] < 1:
        raise ApiBadRequest("targetQuantity must be a positive integer")

    offer['id'] = str(uuid4())
    offer['owners'] = [public_key]
    offer['status'] = "OPEN"

    return offer
