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

const forms = require('../components/forms')
const api = require('../services/api')

const accountSubmitter = state => e => {
  e.preventDefault()

  const accountKeys = ['email', 'password', 'label', 'description']
  const account = _.pick(state, accountKeys)

  api.post('accounts', account)
    .then(res => api.setAuth(res.authorization))
    .then(() => m.route.set('/'))
    .catch(api.alertError)
}

/**
 * The Form for creating a new Account.
 */
const SignupForm = {
  view (vnode) {
    const setter = forms.stateSetter(vnode.state)

    return m('.signup-form', [
      m('form', { onsubmit: accountSubmitter(vnode.state) },
      m('legend', 'Create Account'),
      forms.emailInput(setter('email'), 'Email'),
      forms.passwordInput(setter('password'), 'Password'),
      forms.textInput(setter('label'), 'Label'),
      forms.textInput(setter('description'), 'Description'),
      m('.container.text-center',
        'Or you can ',
        m('a[href="/login"]',
          { oncreate: m.route.link },
          'login with an existing Account')),
      m('.form-group',
        m('.row.justify-content-end.align-items-end',
          m('col-2',
            m('button.btn.btn-primary',
              'Create Account')))))
    ])
  }
}

module.exports = SignupForm
