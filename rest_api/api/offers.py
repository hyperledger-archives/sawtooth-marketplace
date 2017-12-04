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

from sanic import Blueprint

from api.authorization import authorized
from api.errors import ApiNotImplemented


OFFERS_BP = Blueprint('offers')


@OFFERS_BP.post('offers')
@authorized()
async def create_offer(request):
    """Creates a new Offer in state"""
    raise ApiNotImplemented()


@OFFERS_BP.get('offers')
async def get_all_offers(request):
    """Fetches complete details of all Offers in state"""
    raise ApiNotImplemented()


@OFFERS_BP.get('offers/<offer_id>')
async def get_offer(request, offer_id):
    """Fetches the details of particular Offer in state"""
    raise ApiNotImplemented()


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
