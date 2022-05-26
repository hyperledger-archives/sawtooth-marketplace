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
from rethinkdb.errors  import ReqlNonExistenceError

r = rdb.RethinkDB()


from api.errors import ApiInternalError


VAL_TYPE_INT = r.expr([
    "REQUIRE_SOURCE_QUANTITIES", "REQUIRE_TARGET_QUANTITIES"
])


def fetch_latest_block_num():
    try:
        return r.table('blocks')\
            .max(index='block_num')\
            .get_field('block_num')
    except ReqlNonExistenceError:
        raise ApiInternalError('No block data found in state')


def fetch_holdings(holding_ids):
    return r.table('holdings')\
        .get_all(r.args(holding_ids), index='id')\
        .filter(lambda holding: (
            fetch_latest_block_num() >= holding['start_block_num'])
                & (fetch_latest_block_num() < holding['end_block_num']))\
        .map(lambda holding: (holding['label'] == "").branch(
            holding.without('label'), holding))\
        .map(lambda holding: (holding['description'] == "").branch(
            holding.without('description'), holding))\
        .without('start_block_num', 'end_block_num', 'delta_id', 'account')\
        .coerce_to('array')


def parse_rules(rules):
    return r.expr(
        {
            'rules': rules.map(lambda rule: (
                rule['value'] == bytes('', 'utf-8')).branch(
                    rule.without('value'),
                    rule.merge(
                        {
                            'value': _value_to_array(rule)
                        })))
        })


def _value_to_array(rule):
    val_array = rule['value'].coerce_to('string').split(",")
    return VAL_TYPE_INT.contains(rule['type']).branch(
        val_array.map(lambda val: val.coerce_to('number')), val_array)
