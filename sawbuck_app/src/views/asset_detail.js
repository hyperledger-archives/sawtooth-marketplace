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
const { createOffer } = require('./create_offer_modal')

const offerButton = (name, key = 'source') => {
  const label = key === 'target' ? 'Request' : 'Offer'
  const onclick = key === 'target'
    ? () => createOffer(null, name)
    : () => createOffer(name)

  return m('button.btn-lg.btn-outline-primary', { onclick }, label)
}

/**
 * Displays information for a particular Account.
 * The information can be edited if the user themself.
 */
const AssetDetailPage = {
  oninit (vnode) {
    const safeName = window.encodeURI(vnode.attrs.name)
    api.get(`assets/${safeName}`)
      .then(asset => {
        vnode.state.asset = asset
        if (asset.owners.length > 0) {
          return api.get(`accounts/${asset.owners[0]}`)
        }
      })
      .then(owner => { if (owner) vnode.state.owner = owner })
  },

  view (vnode) {
    const asset = _.get(vnode.state, 'asset', {})
    const owner = _.get(vnode.state, 'owner', {})
    const rules = asset.rules || []
    const ownerName = owner.label || owner.publicKey

    return [
      layout.title(asset.name),
      layout.description(_.get(vnode.state, 'asset.description', '')),
      m('.container',
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
            : m('em', 'this asset has no special rules'))),
        m('.row.text-center.mt-5',
          m('.col-md.m-3', offerButton(asset.name)),
          m('.col-md.m-3', offerButton(asset.name, 'target'))))
    ]
  }
}

module.exports = AssetDetailPage
