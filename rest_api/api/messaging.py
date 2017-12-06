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

from sawtooth_rest_api.protobuf import client_batch_submit_pb2
from sawtooth_rest_api.protobuf import validator_pb2

from api.errors import ApiBadRequest
from api.errors import ApiInternalError


async def send(conn, timeout, batches):
    batch_request = client_batch_submit_pb2.ClientBatchSubmitRequest()
    batch_request.batches.extend(batches)

    validator_response = await conn.send(
        validator_pb2.Message.CLIENT_BATCH_SUBMIT_REQUEST,
        batch_request.SerializeToString(),
        timeout)

    client_response = client_batch_submit_pb2.ClientBatchSubmitResponse()
    client_response.ParseFromString(validator_response.content)

    if client_response == client_batch_submit_pb2.ClientBatchStatus.COMMITTED:
        return client_response
    elif client_response == client_batch_submit_pb2.ClientBatchStatus.INVALID:
        raise ApiBadRequest(
            "Bad Request: {}".format(
                client_response.invalid_transactions[0].message))
    elif client_response == client_batch_submit_pb2.ClientBatchStatus.PENDING:
        raise ApiInternalError(
            "Internal Error: Transaction submitted but timed out")
    elif client_response == client_batch_submit_pb2.ClientBatchStatus.UNKNOWN:
        raise ApiInternalError(
            "Internal Error: Something went wrong. Try again later")
