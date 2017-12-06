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

from functools import wraps

from itsdangerous import BadSignature

from sanic import Blueprint

from api import common
from api.errors import ApiNotImplemented
from api.errors import ApiUnauthorized
from db import auth_query


AUTH_BP = Blueprint('auth')


@AUTH_BP.post('authorization')
async def authorization(request):
    """Requests an authorization token for a registered Account"""
    raise ApiNotImplemented()


def authorized():
    """Verifies that the token is valid and belongs to an existing user"""
    def decorator(func):
        @wraps(func)
        async def decorated_function(request, *args, **kwargs):
            if request.token is None:
                raise ApiUnauthorized("Unauthorized: No bearer token provided")
            try:
                email = common.deserialize_auth_token(
                    request.app.config.SECRET_KEY,
                    request.token).get('email')
                auth_info = await auth_query.fetch_info_by_email(
                    request.app.config.DB_CONN, email)
                if auth_info is None:
                    raise ApiUnauthorized(
                        "Unauthorized: "
                        "Token does not belong to an existing user")
            except BadSignature:
                raise ApiUnauthorized("Unauthorized: Invalid bearer token")
            response = await func(request, *args, **kwargs)
            return response
        return decorated_function
    return decorator
