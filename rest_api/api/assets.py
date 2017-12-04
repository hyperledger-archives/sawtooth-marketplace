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


ASSETS_BP = Blueprint('assets')


@ASSETS_BP.post('assets')
@authorized()
async def create_asset(request):
    """Creates a new Asset in state"""
    raise ApiNotImplemented()


@ASSETS_BP.get('assets')
async def get_all_assets(request):
    """Fetches complete details of all Assets in state"""
    raise ApiNotImplemented()


@ASSETS_BP.get('assets/<name>')
async def get_asset(request, name):
    """Fetches the details of particular Asset in state"""
    raise ApiNotImplemented()
