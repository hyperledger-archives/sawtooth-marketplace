# Copyright 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------------

from marketplace_addressing import addresser
from marketplace_processor.protobuf import account_pb2


class MarketplaceState(object):

    def __init__(self, context, timeout=2):
        self._context = context
        self._timeout = timeout
        self._state_entries = None

    def get_account(self, public_key):
        address = addresser.make_account_address(account_id=public_key)

        self._state_entries = self._context.get_state(
            addresses=[address],
            timeout=self._timeout)

        container = _get_account_container(self._state_entries, address)
        account = None
        try:
            account = _get_account_from_container(
                container,
                identifier=public_key)
        except KeyError:
            # We are fine with returning None for an account that doesn't
            # exist in state.
            pass
        return account

    def set_account(self, public_key, label, description, holdings):
        address = addresser.make_account_address(account_id=public_key)

        container = _get_account_container(self._state_entries, address)

        try:
            account = _get_account_from_container(
                container,
                public_key)
        except KeyError:
            account = container.entries.add()

        account.public_key = public_key
        account.label = label
        account.description = description
        for holding in holdings:
            account.holdings.append(holding)

        state_entries_send = {}
        state_entries_send[address] = container.SerializeToString()
        return self._context.set_state(
            state_entries_send,
            self._timeout)


def _get_account_container(state_entries, address):
    try:
        entry = _find_in_state(state_entries, address)
        container = account_pb2.AccountContainer()
        container.ParseFromString(entry.data)
    except KeyError:
        container = account_pb2.AccountContainer()

    return container


def _get_account_from_container(container, identifier):
    for account in container.entries:
        if account.public_key == identifier:
            return account
    raise KeyError(
        "Account with identifier {} is not in container.".format(identifier))


def _find_in_state(state_entries, address):
    for entry in state_entries:
        if entry.address == address:
            return entry
    raise KeyError("Address {} not found in state".format(address))
