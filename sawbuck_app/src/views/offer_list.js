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
const api = require('../services/api')
const layout = require('../components/layout')
const mkt = require('../components/marketplace')
const { acceptOffer } = require('./accept_offer_modal')

const filterDropdown = (label, assets, setter) => {
  const options = assets.map(asset => ({
    text: asset,
    onclick: setter(asset)
  }))
  options.push({
    text: m('em', 'clear filter'),
    onclick: setter(null)
  })

  return layout.dropdown(label, options, 'success')
}

const acceptButton = (offer, account = null) => {
  const onclick = () => acceptOffer(offer.id)
  let disabled = false
  if (!account) disabled = true
  else if (offer.targetQuantity === 0) disabled = false
  else if (!account.quantities[offer.targetAsset]) disabled = true
  else if (account.quantities[offer.targetAsset] < offer.targetQuantity) {
    disabled = true
  }

  return m(
    `button.btn.btn-lg.btn-outline-${disabled ? 'secondary' : 'primary'}`,
    { onclick, disabled },
    'Accept')
}

const offerRow = account => offer => {
  return [
    m('.row.my-2',
      m('.col-md-9',
        m('a.h5', {
          href: `/offers/${offer.id}`,
          oncreate: m.route.link
        }, offer.label || offer.id)),
      m('.col-md-3.text-right', acceptButton(offer, account))),
    mkt.bifold({
      header: offer.sourceAsset,
      body: offer.sourceQuantity
    }, {
      header: offer.targetAsset,
      body: offer.targetQuantity || 'free'
    })
  ]
}

const pluckUniq = (items, key) => _.uniq(items.map(item => item[key]))

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

        // If logged in, save account to state with asset quantities
        const publicKey = api.getPublicKey()
        if (publicKey) {
          const account = accounts
            .find(account => account.publicKey === publicKey)

          const quantities = acct.getAssetQuantities(account)
          vnode.state.account = _.assign({ quantities }, account)
        }
      })
      .catch(api.ignoreError)
  },

  view (vnode) {
    let offers = _.get(vnode.state, 'offers', [])
    const sourceAssets = pluckUniq(offers, 'sourceAsset')
    const targetAssets = pluckUniq(offers, 'targetAsset')

    if (vnode.state.source) {
      offers = offers.filter(offer => {
        return offer.sourceAsset === vnode.state.source
      })
    }

    if (vnode.state.target) {
      offers = offers.filter(offer => {
        return offer.targetAsset === vnode.state.target
      })
    }

    return [
      layout.title('Available Offers'),
      m('.container',
        m('.row.text-center.my-4',
          m('.col-md-5',
            filterDropdown(
              vnode.state.source || 'Offered',
              sourceAssets,
              asset => () => { vnode.state.source = asset })),
          m('.col-md-2'),
          m('.col-md-5',
            filterDropdown(
              vnode.state.target || 'Requested',
              targetAssets,
              asset => () => { vnode.state.target = asset }))),
        offers.length > 0
          ? offers.map(offerRow(vnode.state.account))
          : m('.text-center.font-italic',
              'there are currently no available offers'))
    ]
  }
}

module.exports = OfferListPage
