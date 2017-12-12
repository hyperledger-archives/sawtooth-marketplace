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

import logging

import rethinkdb as r

from api.errors import ApiBadRequest


LOGGER = logging.getLogger(__name__)


async def create_auth_entry(conn, auth_entry):
    result = await r.table('auth').insert(auth_entry).run(conn)
    if result.get('errors') > 0 and \
       "Duplicate primary key `email`" in result.get('first_error'):
        raise ApiBadRequest("A user with that email already exists")


async def remove_auth_entry(conn, email):
    await r.table('auth').get(email).delete().run(conn)


async def fetch_info_by_email(conn, email):
    return await r.table('auth').get(email).run(conn)


async def update_auth_info(conn, email, public_key, update):
    result = await r.table('auth')\
        .get(email)\
        .do(lambda auth_info: r.expr(update.get('email')).branch(
            r.expr(r.table('auth').insert(auth_info.merge(update),
                                          return_changes=True)),
            r.table('auth').get(email).update(update, return_changes=True)))\
        .do(lambda auth_info: auth_info['errors'].gt(0).branch(
            auth_info,
            auth_info['changes'][0]['new_val'].pluck('email')))\
        .merge(_fetch_account_info(public_key))\
        .run(conn)
    if result.get('errors'):
        if "Duplicate primary key `email`" in result.get('first_error'):
            raise ApiBadRequest(
                "Bad Request: A user with that email already exists")
        else:
            raise ApiBadRequest(
                "Bad Request: {}".format(result.get('first_error')))
    if update.get('email'):
        await remove_auth_entry(conn, email)
    return result


def _fetch_account_info(public_key):
    return r.table('accounts')\
        .get_all(public_key, index='public_key')\
        .max('start_block_num')\
        .do(lambda account: account.merge(
            {'publicKey': account['public_key']}))\
        .do(lambda account: (account['label'] == "").branch(
            account.without('label'), account))\
        .do(lambda account: (account['description'] == "").branch(
            account.without('description'), account))\
        .without('public_key', 'delta_id',
                 'start_block_num', 'end_block_num')
