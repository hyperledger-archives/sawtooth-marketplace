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
const forms = require('../components/forms')
const layout = require('../components/layout')
const mkt = require('../components/marketplace')
const modals = require('../components/modals')

// Returns a label string, truncated if necessary
const truncatedLabel = (value, defaultValue, max = 10) => {
  const label = value || defaultValue
  if (label.length <= max) return label
  return `${label.slice(0, max - 3)}...`
}

// Returns a green check mark if visible
const checkMark = (isVisible = true) => {
  return m(`span.text-${isVisible ? 'success' : 'white'}`,
           layout.icon('check'),
           ' ')
}

// Small fields with placeholders rather than headers, for new holdings
const holdingField = (placeholder, onValue) => {
  return forms.field(onValue, { placeholder, required: false })
}

// Returns a function which sets id, label, and new for outgoing holdings
const outSetter = state => holding => () => {
  state.acceptance.out = holding.id
  state.outLabel = holding.asset
  state.outMax = holding.quantity
}

// Returns a function which sets id and label keys for the incoming holdings
const inSetter = state => (holding, hasNew) => () => {
  state.acceptance.in = holding.id
  state.inLabel = holding.asset
  state.hasNewHolding = hasNew
}

const countSetter = state => inQuantity => {
  let count = Math.floor(inQuantity / state.offer.sourceQuantity)
  if (inQuantity !== 0) count = Math.max(count, 1)

  const exchangeOnce = state.offer.rules.find(({ type }) => {
    return type.slice(0, 13) === 'EXCHANGE_ONCE'
  })
  if (exchangeOnce) count = Math.min(count, 1)

  if (count * state.offer.sourceQuantity > state.inMax) {
    count = Math.floor(state.inMax / state.offer.sourceQuantity)
  }

  if (count * state.offer.targetQuantity > state.outMax) {
    count = Math.floor(state.outMax / state.offer.targetQuantity)
  }

  state.acceptance.count = count
  state.inQuantity = count * state.offer.sourceQuantity
  state.outQuantity = count * state.offer.targetQuantity
}

// Returns a function to map holding data to dropdown options
const optionMapper = (state, key = 'in') => {
  const setter = key !== 'out' ? inSetter(state) : outSetter(state)

  return holding => ({
    isSelected: () => state.acceptance[key] === holding.id,
    text: `${holding.asset} (${holding.label || holding.id})`,
    onclick: setter(holding, false)
  })
}

// Returns a dropdown option which will trigger holding creation
const newOption = state => ({
  isSelected: () => !!state.hasNewHolding,
  text: m('em', 'new (New Holding)'),
  onclick: inSetter(state)({ asset: 'new' }, true)
})

// Adds a check mark to the appropriate holding option
const checkMarkMapper = (state, key = 'in') => option => {
  return _.assign({}, option, {
    text: [
      checkMark(option.isSelected()),
      option.text
    ]
  })
}

// Returns true or false depending on whether or not the form is valid
const isFormValid = state => !!state.acceptance.count

// Returns a function which will submit a new offer, and holding if applicable
const submitter = (state, onDone) => () => {
  return Promise.resolve()
    .then(() => {
      if (state.hasNewHolding) {
        const holdingKeys = ['label', 'description', 'asset']
        return api.post('holdings', _.pick(state.holding, holdingKeys))
      }
    })
    .then(holding => {
      const acceptance = {
        count: state.acceptance.count,
        target: state.acceptance.in
      }
      if (state.acceptance.out) acceptance.source = state.acceptance.out
      if (holding) acceptance.target = holding.id
      return api.patch(`offers/${state.offer.id}/accept`, acceptance)
    })
    .then(onDone)
    .then(() => m.route.set('/account'))
    .then(() => new Promise(resolve => setTimeout(resolve, 2000)))
    .then(() => window.location.reload())
    .catch(api.alertError)
}

const getAsset = (id, holdings) => {
  return holdings.find(holding => holding.id === id).asset
}

// A versatile modal allowing users to create new offers (and new holdings)
const AcceptOfferModal = {
  oninit (vnode) {
    vnode.state.holding = {}
    vnode.state.acceptance = {}
    vnode.state.hasNewHolding = false

    api.get(`offers/${vnode.attrs.offerId}`)
      .then(offer => {
        if (offer.error) return console.error(offer.error)
        vnode.state.offer = offer

        return Promise.all([
          acct.getUserAccount(),
          api.get(`accounts/${offer.owners[0]}`)
        ])
      })
      .then(([ user, owner ]) => {
        const inAsset = getAsset(vnode.state.offer.source, owner.holdings)
        vnode.state.holding.asset = inAsset
        vnode.state.inOptions = user.holdings
          .filter(holding => holding.asset === inAsset)
          .map(optionMapper(vnode.state))
          .concat(newOption(vnode.state))
        vnode.state.inOptions[0].onclick()

        if (vnode.state.offer.target) {
          const outAsset = getAsset(vnode.state.offer.target, owner.holdings)
          vnode.state.outOptions = user.holdings
            .filter(holding => holding.asset === outAsset)
            .map(optionMapper(vnode.state, 'out'))
          vnode.state.outOptions[0].onclick()
        } else {
          vnode.state.outLabel = 'free'
        }

        // Set initial count/quantity values to the minimum exchange
        countSetter(vnode.state)(1)

        return Promise.all([ owner, api.get(`assets/${inAsset}`) ])
      })
      .then(([ owner, inAsset ]) => {
        const allInfinite = inAsset.rules.find(({ type }) => {
          return type === 'ALL_HOLDINGS_INFINITE'
        })
        const ownerInfinite = inAsset.rules.find(({ type }) => {
          return type === 'OWNER_HOLDINGS_INFINITE'
        })
        const isOwner = owner.publicKey === inAsset.owners[0].publicKey

        vnode.state.inMax = allInfinite || (ownerInfinite && isOwner)
          ? Number.MAX_SAFE_INTEGER
          : owner.holdings
            .find(holding => holding.id === vnode.state.offer.source)
            .quantity
      })
  },

  view (vnode) {
    const setter = path => value => _.set(vnode.state, path, value)
    const inOptions = _.get(vnode.state, 'inOptions', [])
      .map(checkMarkMapper(vnode.state))
    const outOptions = _.get(vnode.state, 'outOptions', [])
      .map(checkMarkMapper(vnode.state, 'out'))

    return modals.base(
      modals.header('Accept Offer', vnode.attrs.cancelFn),
      modals.body(
        m('.container', [
          m('.text-muted.mb-2',
            `Enter how much ${vnode.state.holding.asset} you would like`),
          mkt.bifold({
            header: layout.dropdown(
              truncatedLabel(vnode.state.inLabel, 'Offered'),
              inOptions,
              'success'),
            body: forms.field(countSetter(vnode.state), {
              type: 'number',
              defaultValue: vnode.state.inQuantity,
              onblur: ({ target }) => { target.value = vnode.state.inQuantity }
            })
          }, {
            header: layout.dropdown(
              truncatedLabel(vnode.state.outLabel, 'Requested'),
              outOptions,
              'success'),
            body: vnode.state.outQuantity || '---'
          }),
          !vnode.state.hasNewHolding
            ? null
            : forms.group('New Holding', layout.row([
              holdingField('Label', setter('holding.label')),
              holdingField('Description', setter('holding.description'))
            ]))
        ])),
      modals.footer(
        modals.button('Cancel', vnode.attrs.cancelFn, 'secondary'),
        modals.button(
          'Accept',
          submitter(vnode.state, vnode.attrs.acceptFn),
          'primary',
          { disabled: !isFormValid(vnode.state) })))
  }
}

/**
 * Displays a modal which will guide the user through accepting an Offer
 */
const acceptOffer = offerId => {
  return modals.show(AcceptOfferModal, { offerId })
    .catch(() => console.log('Accepting offer canceled'))
}

module.exports = { acceptOffer }
