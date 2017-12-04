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

from api.errors import ApiNotImplemented


ACCOUNTS_BP = Blueprint('accounts')


@ACCOUNTS_BP.post('accounts')
async def create_account(request):
    """Creates a new Account and corresponding authorization token"""
    raise ApiNotImplemented()


@ACCOUNTS_BP.get('accounts')
async def get_all_accounts(request):
    """Fetches complete details of all Accounts in state"""
    raise ApiNotImplemented()


@ACCOUNTS_BP.get('accounts/<account_id>')
async def get_account(request, account_id):
    """Fetches the details of particular Account in state"""
    raise ApiNotImplemented()
