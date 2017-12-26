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

// Returns a string of bullets
const bullets = count => _.fill(Array(count), '•').join('')

// Basis for info fields with headers
const labeledField = (header, field) => {
  return m('.field-group.mt-5', header, field)
}

const fieldHeader = (label, ...additions) => {
  return m('.field-header', [
    m('span.h5.mr-3', label),
    additions
  ])
}

// Simple info field with a label
const staticField = (label, info) => labeledField(fieldHeader(label), info)

const toggledInfo = (isToggled, initialView, toggledView) => {
  return m('.field-info', isToggled ? toggledView : initialView)
}

// An in-line form for updating a single field
const infoForm = (state, key, onSubmit, opts) => {
  return m('form.form-inline', {
    onsubmit: () => onSubmit().then(() => { state.toggled[key] = false })
  }, [
    m('input.form-control-sm.mr-1', _.assign({
      oninput: m.withAttr('value', value => { state.update[key] = value })
    }, opts)),
    m('button.btn.btn-secondary.btn-sm.mr-1', {
      onclick: () => { state.toggled[key] = false }
    }, 'Cancel'),
    m('button.btn.btn-primary.btn-sm.mr-1', { type: 'submit' }, 'Update')
  ])
}

// Pencil icon that simply toggles visibility
const editIcon = (obj, key) => {
  return forms.clickIcon('pencil', () => { obj[key] = !obj[key] })
}

// Edits a field in state
const editField = (state, label, key) => {
  const currentInfo = _.get(state, ['account', key], '')
  const onSubmit = () => {
    return api.patch('accounts', _.pick(state.update, key))
      .then(() => { state.account[key] = state.update[key] })
      .catch(api.alertError)
  }

  return labeledField(
    fieldHeader(label, editIcon(state.toggled, key)),
    toggledInfo(
      state.toggled[key],
      currentInfo,
      infoForm(state, key, onSubmit, {placeholder: currentInfo})))
}

const passwordField = state => {
  const onSubmit = () => {
    return api.patch('accounts', {
      password: state.update.password
    })
      .then(() => m.redraw())
      .catch(api.alertError)
  }

  return labeledField(
    fieldHeader('Password', editIcon(state.toggled, 'password')),
    toggledInfo(
      state.toggled.password,
      bullets(16),
      infoForm(state, 'password', onSubmit, { type: 'password' })))
}

const holdingRow = holding => {
  return m('.row.mt-3', [
    m('.col-md-7',
      layout.row(m('h6', holding.label)),
      layout.row(m('.text-muted', holding.description))),
    m('.col-md-5',
      mkt.holding(holding.asset, holding.quantity))
  ])
}

/**
 * Displays information for a particular Account.
 * The information can be edited if the user themself.
 */
const AccountDetailPage = {
  oninit (vnode) {
    vnode.state.toggled = {}
    vnode.state.update = {}

    Promise.resolve()
      .then(() => {
        if (vnode.attrs.publicKey === api.getPublicKey()) {
          return acct.getUserAccount()
        }
        return api.get(`accounts/${vnode.attrs.publicKey}`)
      })
      .then(account => {
        vnode.state.account = account
        m.redraw()
      })
      .catch(api.ignoreError)
  },

  view (vnode) {
    const publicKey = _.get(vnode.state, 'account.publicKey', '')
    const holdings = _.get(vnode.state, 'account.holdings', [])

    const profileContent = layout.row([
      editField(vnode.state, 'Email', 'email'),
      passwordField(vnode.state)
    ])

    return [
      layout.title(_.get(vnode.state, 'account.label', '')),
      layout.description(_.get(vnode.state, 'account.description', '')),
      m('.container',
        publicKey === api.getPublicKey() ? profileContent : null,
        layout.row(staticField('Public Key', publicKey)),
        layout.row(staticField(
          'Holdings',
          holdings.length > 0
            ? holdings.map(holdingRow)
            : m('em', 'this account currently has no holdings'))))
    ]
  }
}

module.exports = AccountDetailPage
