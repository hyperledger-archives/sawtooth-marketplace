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

const api = require('../services/api')
const layout = require('../components/layout')
const mkt = require('../components/marketplace')

const acceptButton = offer => {
  const onclick = () => console.log(`Accepting offer ${offer.id}...`)

  return m(
    'button.btn.btn-lg.btn-outline-primary.mr-3',
    { onclick },
    'Accept')
}

const offerRow = offer => {
  return [
    m('.row.my-2',
      m('.col-md-9',
        m('a.h5', {
          href: `/offers/${offer.id}`,
          oncreate: m.route.link
        }, offer.label || offer.id)),
      m('.col-md-3.text-right', acceptButton(offer))),
    mkt.bifold({
      header: offer.sourceAsset,
      body: offer.sourceQuantity
    }, {
      header: offer.targetAsset,
      body: offer.targetQuantity || 'free'
    })
  ]
}

/**
 * A page displaying each Asset, with links to create an Offer,
 * or to view more detail.
 */
const OfferListPage = {
  oninit (vnode) {
    Promise.all([api.get('offers'), api.get('accounts')])
      .then(([ offers, accounts ]) => {
        // Pair each holding with its asset type
        const holdingAssets = _.chain(accounts)
          .map(account => account.holdings)
          .flatten()
          .reduce((holdingAssets, holding) => {
            holdingAssets[holding.id] = holding.asset
            return holdingAssets
          }, {})
          .value()

        // Save offers to state with asset names
        vnode.state.offers = offers.map(offer => {
          return _.assign({
            sourceAsset: holdingAssets[offer.source],
            targetAsset: holdingAssets[offer.target]
          }, offer)
        })
      })
  },

  view (vnode) {
    const offers = _.get(vnode.state, 'offers', [])

    return [
      layout.title('Available Offers'),
      m('.container',
        offers.length > 0
          ? offers.map(offerRow)
          : m('.text-center.font-italic',
              'there are currently no available offers'))
    ]
  }
}

module.exports = OfferListPage
