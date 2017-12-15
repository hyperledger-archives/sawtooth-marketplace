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

import rethinkdb as r
from rethinkdb.errors import ReqlNonExistenceError

from api.errors import ApiBadRequest

from db.common import fetch_holdings
from db.common import fetch_latest_block_num


async def fetch_all_account_resources(conn):
    return await r.table('accounts')\
        .filter((fetch_latest_block_num() >= r.row['start_block_num'])
                & (fetch_latest_block_num() < r.row['end_block_num']))\
        .map(lambda account: account.merge(
            {'publicKey': account['public_key']}))\
        .map(lambda account: account.merge(
            {'holdings': fetch_holdings(account['holdings'])}))\
        .map(lambda account: (account['label'] == "").branch(
            account.without('label'), account))\
        .map(lambda account: (account['description'] == "").branch(
            account.without('description'), account))\
        .without('public_key', 'delta_id',
                 'start_block_num', 'end_block_num')\
        .coerce_to('array').run(conn)


async def fetch_account_resource(conn, public_key, auth_key):
    try:
        return await r.table('accounts')\
            .get_all(public_key, index='public_key')\
            .max('start_block_num')\
            .merge({'publicKey': r.row['public_key']})\
            .merge({'holdings': fetch_holdings(r.row['holdings'])})\
            .do(lambda account: (r.expr(auth_key).eq(public_key)).branch(
                account.merge(_fetch_email(public_key)), account))\
            .do(lambda account: (account['label'] == "").branch(
                account.without('label'), account))\
            .do(lambda account: (account['description'] == "").branch(
                account.without('description'), account))\
            .without('public_key', 'delta_id',
                     'start_block_num', 'end_block_num')\
            .run(conn)
    except ReqlNonExistenceError:
        raise ApiBadRequest(
            "No account with the public key {} exists".format(public_key))


def _fetch_email(public_key):
    return r.table('auth')\
        .get_all(public_key, index='public_key')\
        .pluck('email')\
        .coerce_to('array')[0]
