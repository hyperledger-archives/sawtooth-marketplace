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

from marketplace_addressing.addresser import address_is
from marketplace_addressing.addresser import AddressSpace
from marketplace_ledger_sync.protobuf.account_pb2 import AccountContainer
from marketplace_ledger_sync.protobuf.asset_pb2 import AssetContainer
from marketplace_ledger_sync.protobuf.holding_pb2 import HoldingContainer
from marketplace_ledger_sync.protobuf.offer_pb2 import OfferContainer


CONTAINERS = {
    AddressSpace.ACCOUNT: AccountContainer,
    AddressSpace.ASSET: AssetContainer,
    AddressSpace.HOLDING: HoldingContainer,
    AddressSpace.OFFER: OfferContainer
}

IGNORE = {
    AddressSpace.OFFER_HISTORY: True
}


def data_to_dicts(address, data):
    """Deserializes a protobuf "container" binary based on its address. Returns
    a list of the decoded objects which were stored at that address.
    """
    data_type = address_is(address)

    if (IGNORE.get(data_type)):
        return []

    try:
        container = CONTAINERS[data_type]
    except KeyError:
        raise TypeError('Unknown data type: {}'.format(data_type))

    entries = _parse_proto(container, data).entries
    return [_proto_to_dict(pb) for pb in entries]


def _parse_proto(proto_class, data):
    deserialized = proto_class()
    deserialized.ParseFromString(data)
    return deserialized


def _proto_to_dict(proto):
    result = {}

    for field in proto.DESCRIPTOR.fields:
        key = field.name
        value = getattr(proto, key)

        if field.type == field.TYPE_MESSAGE:
            if field.label == field.LABEL_REPEATED:
                result[key] = [_proto_to_dict(p) for p in value]
            else:
                result[key] = _proto_to_dict(value)

        elif field.type == field.TYPE_ENUM:
            number = int(value)
            name = field.enum_type.values_by_number.get(number).name
            result[key] = name

        else:
            result[key] = value

    return result
