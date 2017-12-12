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
    await conn.send(
        validator_pb2.Message.CLIENT_BATCH_SUBMIT_REQUEST,
        batch_request.SerializeToString(),
        timeout)


async def check_batch_status(conn, batch_id):
    status_request = client_batch_submit_pb2.ClientBatchStatusRequest(
        batch_ids=[batch_id], wait=True)
    validator_response = await conn.send(
        validator_pb2.Message.CLIENT_BATCH_STATUS_REQUEST,
        status_request.SerializeToString())

    status_response = client_batch_submit_pb2.ClientBatchStatusResponse()
    status_response.ParseFromString(validator_response.content)
    batch_status = status_response.batch_statuses[0].status
    if batch_status == client_batch_submit_pb2.ClientBatchStatus.INVALID:
        invalid = status_response.batch_statuses[0].invalid_transactions[0]
        raise ApiBadRequest(invalid.message)
    elif batch_status == client_batch_submit_pb2.ClientBatchStatus.PENDING:
        raise ApiInternalError("Transaction submitted but timed out")
    elif batch_status == client_batch_submit_pb2.ClientBatchStatus.UNKNOWN:
        raise ApiInternalError("Something went wrong. Try again later")
