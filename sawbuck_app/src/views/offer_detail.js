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

const findAsset = (id, holdings) => holdings.find(h => h.id === id).asset

const acceptButton = (label, onclick, disabled = false) => {
  return m(`button.btn-lg.btn-outline-${disabled ? 'secondary' : 'primary'}`,
           { onclick, disabled },
           label)
}

/**
 * Displays information for a particular Account.
 * The information can be edited if the user themself.
 */
const OfferDetailPage = {
  oninit (vnode) {
    Promise.all([
      api.get(`offers/${vnode.attrs.id}`),
      acct.getUserAccount()
    ])
      .then(([ offer, user ]) => {
        vnode.state.offer = offer

        if (!user) {
          vnode.state.disabled = true
        } else if (offer.targetQuantity === 0) {
          vnode.state.disabled = false
        } else {
          const quantities = acct.getAssetQuantities(user)

          if (!quantities[offer.targetAsset]) {
            vnode.state.disabled = true
          } else if (quantities[offer.targetAsset] < offer.targetQuantity) {
            vnode.state.disabled = true
          } else {
            vnode.state.disabled = false
          }
        }

        const owner = offer.owners[0]
        if (user && user.publicKey === owner) return user
        return api.get(`accounts/${owner}`)
      })
      .then(owner => {
        if (!owner || owner.error) return
        const offer = vnode.state.offer
        offer.sourceAsset = findAsset(offer.source, owner.holdings)
        offer.targetAsset = findAsset(offer.target, owner.holdings)
        vnode.state.owner = owner
      })
      .catch(api.ignoreError)
  },

  view (vnode) {
    const offer = _.get(vnode.state, 'offer', {})
    const owner = _.get(vnode.state, 'owner', {})
    const name = offer.label || offer.id
    const rules = offer.rules || []
    const ownerName = owner.label || owner.publicKey

    return [
      layout.title(name),
      layout.description(offer.description),
      m('.container',
        mkt.bifold({
          header: offer.sourceAsset,
          body: offer.sourceQuantity
        }, {
          header: offer.targetAsset,
          body: offer.targetQuantity || m('em', 'free')
        }),
        layout.row(layout.labeledField(
          'Administered by',
          m('a', {
            href: `/accounts/${owner.publicKey}`,
            oncreate: m.route.link
          }, ownerName))),
        layout.row(layout.labeledField(
          'Rules',
          rules.length > 0
            ? layout.sectionedRows(rules.map(mkt.rule))
            : m('em', 'this offer has no special rules'))),
        m('.row.text-center.mt-5',
          m('.col-md.m-3',
            acceptButton(
              name,
              () => acceptOffer(offer.id),
              vnode.state.disabled))))
    ]
  }
}

module.exports = OfferDetailPage
