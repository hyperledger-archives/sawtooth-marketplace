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

const m = require('mithril')
const _ = require('lodash')

const acct = require('../services/account')
const layout = require('../components/layout')
const api = require('../services/api')
const { createOffer } = require('./create_offer_modal')

const offerButton = (name, disabled, key = 'source') => {
  const label = key === 'target' ? 'Request' : 'Offer'
  const onclick = key === 'target'
    ? () => createOffer(null, name)
    : () => createOffer(name)

  return m(`button.btn.btn-outline-${disabled ? 'secondary' : 'primary'}.mr-3`,
           { onclick, disabled },
           label)
}

const assetRowMapper = account => asset => {
  const safeName = window.encodeURI(asset.name)
  const offerDisabled = !account ||
    !account.quantities[asset.name] ||
    (asset.rules.find(({ type }) => type === 'NOT_TRANSFERABLE') &&
      !asset.owners.find(owner => owner === account.publicKey))
  const requestDisabled = !account

  return m('.row.mb-5', [
    m('.col-md-8', [
      layout.row(m('a.h5', {
        href: `/assets/${safeName}`,
        oncreate: m.route.link
      }, asset.name)),
      layout.row(m('.text-muted', asset.description))
    ]),
    m('.col-md-4.mt-3', [
      offerButton(asset.name, offerDisabled),
      offerButton(asset.name, requestDisabled, 'target')
    ])
  ])
}

/**
 * A page displaying each Asset, with links to create an Offer,
 * or to view more detail.
 */
const AssetListPage = {
  oninit (vnode) {
    Promise.all([ acct.getUserAccount(), api.get(`assets`) ])
      .then(([ account, assets ]) => {
        vnode.state.assets = assets

        if (account) {
          const quantities = acct.getAssetQuantities(account)
          vnode.state.account = _.assign({ quantities }, account)
        }
      })
      .catch(api.ignoreError)
  },

  view (vnode) {
    const assets = _.get(vnode.state, 'assets', [])

    return [
      layout.title('Assets Available'),
      m('.container.mt-6',
        assets.length > 0
          ? assets.map(assetRowMapper(vnode.state.account))
          : m('.text-center',
              m('em', 'there are currently no available assets')))
    ]
  }
}

module.exports = AssetListPage
