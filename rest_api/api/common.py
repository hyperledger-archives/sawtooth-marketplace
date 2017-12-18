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
# ------------------------------------------------------------------------------

from Crypto.Cipher import AES

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from sawtooth_signing import CryptoFactory
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from api.errors import ApiBadRequest

from db import auth_query

from marketplace_transaction.protobuf import rule_pb2


def validate_fields(required_fields, request_json):
    try:
        for field in required_fields:
            if request_json.get(field) is None:
                raise ApiBadRequest("{} is required".format(field))
    except (ValueError, AttributeError):
        raise ApiBadRequest("Improper JSON format")


def encrypt_private_key(aes_key, public_key, private_key):
    init_vector = bytes.fromhex(public_key[:32])
    cipher = AES.new(bytes.fromhex(aes_key), AES.MODE_CBC, init_vector)
    return cipher.encrypt(private_key)


def decrypt_private_key(aes_key, public_key, encrypted_private_key):
    init_vector = bytes.fromhex(public_key[:32])
    cipher = AES.new(bytes.fromhex(aes_key), AES.MODE_CBC, init_vector)
    return cipher.decrypt(encrypted_private_key)


async def get_signer(request):
    email = deserialize_auth_token(
        request.app.config.SECRET_KEY, request.token).get('email')
    auth_info = await auth_query.fetch_info_by_email(
        request.app.config.DB_CONN, email)
    private_key_hex = decrypt_private_key(
        request.app.config.AES_KEY,
        auth_info.get('public_key'),
        auth_info.get('encrypted_private_key'))
    private_key = Secp256k1PrivateKey.from_hex(private_key_hex)
    return CryptoFactory(request.app.config.CONTEXT).new_signer(private_key)


def generate_auth_token(secret_key, email, public_key):
    serializer = Serializer(secret_key)
    token = serializer.dumps({'email': email, 'public_key': public_key})
    return token.decode('ascii')


def deserialize_auth_token(secret_key, token):
    serializer = Serializer(secret_key)
    return serializer.loads(token)


def proto_wrap_rules(rules):
    rule_protos = []
    if rules is not None:
        for rule in rules:
            try:
                rule_proto = rule_pb2.Rule(type=rule['type'])
            except IndexError:
                raise ApiBadRequest("Improper rule format")
            except ValueError:
                raise ApiBadRequest("Invalid rule type")
            except KeyError:
                raise ApiBadRequest("Rule type is required")
            if rule.get('value') is not None:
                rule_proto.value = value_to_csv(rule['value'])
            rule_protos.append(rule_proto)
    return rule_protos


def value_to_csv(value):
    if isinstance(value, (list, tuple)):
        csv = ",".join(map(str, value))
        return bytes(csv, 'utf-8')
    else:
        raise ApiBadRequest("Rule value must be a JSON array")
