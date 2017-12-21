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

const api = require('./api')
let account = null

/**
 * Returns the account of the user if logged in, cached for future requests
 */
const getUserAccount = () => {
  return Promise.resolve()
    .then(() => {
      const publicKey = api.getPublicKey()
      if (!publicKey) return null
      if (account && account.publicKey === publicKey) return account
      return api.get(`accounts/${publicKey}`)
    })
    .then(acct => {
      account = acct
      return acct
    })
}

/**
 * Returns an object with each asset an account has holdings of as the keys
 * the largest quantity of those holdings as the value.
 */
const getAssetQuantities = account => {
  return account.holdings
    .reduce((quantities, { asset, quantity }) => {
      if (!quantities[asset]) quantities[asset] = quantity
      else quantities[asset] = Math.max(quantities[asset], quantity)
      return quantities
    }, {})
}

module.exports = {
  getUserAccount,
  getAssetQuantities
}
