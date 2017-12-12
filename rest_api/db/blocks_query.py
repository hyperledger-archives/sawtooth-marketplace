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
from rethinkdb import ReqlNonExistenceError

from api.errors import ApiInternalError


def latest_block_num():
    try:
        return r.table('blocks')\
            .max(index='block_num')\
            .get_field('block_num')
    except ReqlNonExistenceError:
        raise ApiInternalError('No block data found in state')
