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

import enum
import hashlib


FAMILY_NAME = 'marketplace'


NS = hashlib.sha512(FAMILY_NAME.encode()).hexdigest()[:6]


class OfferHistorySpace(enum.IntEnum):
    START = 0
    STOP = 1


class AssetSpace(enum.IntEnum):
    START = 1
    STOP = 50


class HoldingSpace(enum.IntEnum):
    START = 50
    STOP = 125


class AccountSpace(enum.IntEnum):
    START = 125
    STOP = 200


class OfferSpace(enum.IntEnum):
    START = 200
    STOP = 256


@enum.unique
class AddressSpace(enum.IntEnum):
    ASSET = 0
    HOLDING = 1
    ACCOUNT = 2
    OFFER = 3
    OFFER_HISTORY = 4

    OTHER_FAMILY = 100


def _hash(identifier):
    return hashlib.sha512(identifier.encode()).hexdigest()


def _compress(address, start, stop):
    return "%.2X".lower() % (int(address, base=16) % (stop - start) + start)


def make_offer_account_address(offer_id, account):
    offer_hash = _hash(offer_id)
    account_hash = _hash(account)

    return NS + '00' + offer_hash[:60] + _compress(account_hash, 1, 256)


def make_offer_history_address(offer_id):
    offer_hash = _hash(offer_id)

    return NS + '00' + offer_hash[:60] + '00'


def make_asset_address(asset_id):
    full_hash = _hash(asset_id)

    return NS + _compress(
        full_hash,
        AssetSpace.START,
        AssetSpace.STOP) + full_hash[:62]


def make_holding_address(holding_id):
    full_hash = _hash(holding_id)

    return NS + _compress(
        full_hash,
        HoldingSpace.START,
        HoldingSpace.STOP) + full_hash[:62]


def make_account_address(account_id):
    full_hash = _hash(account_id)

    return NS + _compress(
        full_hash,
        AccountSpace.START,
        AccountSpace.STOP) + full_hash[:62]


def make_offer_address(offer_id):
    full_hash = _hash(offer_id)

    return NS + _compress(
        full_hash,
        OfferSpace.START,
        OfferSpace.STOP) + full_hash[:62]


def _contains(num, space):
    return space.START <= num < space.STOP


def address_is(address):

    if address[:len(NS)] != NS:
        return AddressSpace.OTHER_FAMILY

    infix = int(address[6:8], 16)

    if _contains(infix, OfferHistorySpace):
        result = AddressSpace.OFFER_HISTORY

    elif _contains(infix, AssetSpace):
        result = AddressSpace.ASSET

    elif _contains(infix, HoldingSpace):
        result = AddressSpace.HOLDING

    elif _contains(infix, AccountSpace):
        result = AddressSpace.ACCOUNT

    elif _contains(infix, OfferSpace):
        result = AddressSpace.OFFER
    else:
        result = AddressSpace.OTHER_FAMILY

    return result
