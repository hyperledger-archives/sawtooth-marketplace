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

import rethinkdb as rdb
from rethinkdb.errors import ReqlNonExistenceError

from api.errors import ApiBadRequest

from db.common import fetch_latest_block_num
from db.common import parse_rules

r = rdb.RethinkDB()

print(">>> ", type(r))
print(">>> ", dir(r))


async def fetch_all_offer_resources(conn, query_params):
    return await r.table('offers')\
        .filter((fetch_latest_block_num() >= r.row['start_block_num'])
                & (fetch_latest_block_num() < r.row['end_block_num']))\
        .filter(query_params)\
        .map(lambda offer: (offer['label'] == "").branch(
            offer.without('label'), offer))\
        .map(lambda offer: (offer['description'] == "").branch(
            offer.without('description'), offer))\
        .map(lambda offer: offer.merge(
            {'sourceQuantity': offer['source_quantity']}))\
        .map(lambda offer: (offer['target'] == "").branch(
            offer.without('target'), offer))\
        .map(lambda offer: (offer['target_quantity'] == "").branch(
            offer,
            offer.merge({'targetQuantity': offer['target_quantity']})))\
        .map(lambda offer: (offer['rules'] == []).branch(
            offer, offer.merge(parse_rules(offer['rules']))))\
        .without('delta_id', 'start_block_num', 'end_block_num',
                 'source_quantity', 'target_quantity')\
        .coerce_to('array').run(conn)


async def fetch_offer_resource(conn, offer_id):
    try:
        return await r.table('offers')\
            .get_all(offer_id, index='id')\
            .max('start_block_num')\
            .do(lambda offer: (offer['label'] == "").branch(
                offer.without('label'), offer))\
            .do(lambda offer: (offer['description'] == "").branch(
                offer.without('description'), offer))\
            .merge({'sourceQuantity': r.row['source_quantity']})\
            .do(lambda offer: (offer['target'] == "").branch(
                offer.without('target'), offer))\
            .do(lambda offer: (offer['target_quantity'] == "").branch(
                offer,
                offer.merge({'targetQuantity': offer['target_quantity']})))\
            .do(lambda offer: (offer['rules'] == []).branch(
                offer, offer.merge(parse_rules(offer['rules']))))\
            .without('delta_id', 'start_block_num', 'end_block_num',
                     'source_quantity', 'target_quantity')\
            .run(conn)
    except ReqlNonExistenceError:
        raise ApiBadRequest("No offer with the id {} exists".format(offer_id))
