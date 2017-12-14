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

/**
 * Returns a simple stylized card element for displaying a holding
 */
const holding = (header, body, color = 'success') => {
  return m(`.card.border-${color}`, [
    m(`.card-header.text-${color}.border-${color}.text-center`,
      {style: 'line-height:0.8;'},
      header),
    m('.card-body', {style: 'line-height:0.2;'},
      m('p.card-text.text-right', m('em', body)))
  ])
}

module.exports = {
  holding
}
