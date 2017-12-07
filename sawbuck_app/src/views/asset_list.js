/**
 * Copyright 2017 Intel Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ----------------------------------------------------------------------------
 */
'use strict'

const _ = require('lodash')

const layout = require('../components/layout')
const api = require('../services/api')

/**
 * A page displaying each Asset, with links to create an Offer,
 * or to view more detail.
 */
const AssetListPage = {
  oninit (vnode) {
    api.get(`assets`)
      .then(assets => { vnode.state.assets = assets })
  },

  view (vnode) {
    const assets = _.get(vnode.state, 'assets', [])

    return [
      layout.title('Assets Available'),
      layout.row(JSON.stringify(assets))
    ]
  }
}

module.exports = AssetListPage
