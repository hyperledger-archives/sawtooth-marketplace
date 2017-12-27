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

import logging

from sawtooth_sdk.messaging.stream import Stream
from sawtooth_sdk.protobuf.validator_pb2 import Message
from sawtooth_sdk.protobuf.events_pb2 import EventList
from sawtooth_sdk.protobuf.events_pb2 import EventSubscription
from sawtooth_sdk.protobuf.events_pb2 import EventFilter
from sawtooth_sdk.protobuf.client_event_pb2 import ClientEventsSubscribeRequest
from sawtooth_sdk.protobuf.client_event_pb2\
    import ClientEventsSubscribeResponse
from sawtooth_sdk.protobuf.client_event_pb2\
    import ClientEventsUnsubscribeRequest
from sawtooth_sdk.protobuf.client_event_pb2\
    import ClientEventsUnsubscribeResponse

from marketplace_addressing.addresser import NS as NAMESPACE


LOGGER = logging.getLogger(__name__)
NULL_BLOCK_ID = '0000000000000000'


class Subscriber(object):
    """Creates an object that can subscribe to state delta events using the
    Sawtooth SDK's Stream class. Handler functions can be added prior to
    subscribing, and each will be called on each delta event received.
    """
    def __init__(self, validator_url):
        LOGGER.info('Connecting to validator: %s', validator_url)
        self._stream = Stream(validator_url)
        self._event_handlers = []
        self._is_active = False

    def add_handler(self, handler):
        """Adds a handler which will be passed state delta events when they
        occur. Note that this event is mutable.
        """
        self._event_handlers.append(handler)

    def clear_handlers(self):
        """Clears any delta handlers.
        """
        self._event_handlers = []

    def start(self, known_ids=None):
        """Subscribes to state delta events, and then waits to receive deltas.
        Sends any events received to delta handlers.
        """
        if not known_ids:
            known_ids = [NULL_BLOCK_ID]

        self._stream.wait_for_ready()
        LOGGER.debug('Subscribing to state delta events')

        block_sub = EventSubscription(event_type='sawtooth/block-commit')
        delta_sub = EventSubscription(
            event_type='sawtooth/state-delta',
            filters=[EventFilter(
                key='address',
                match_string='^{}.*'.format(NAMESPACE),
                filter_type=EventFilter.REGEX_ANY)])

        request = ClientEventsSubscribeRequest(
            last_known_block_ids=known_ids,
            subscriptions=[block_sub, delta_sub])
        response_future = self._stream.send(
            Message.CLIENT_EVENTS_SUBSCRIBE_REQUEST,
            request.SerializeToString())
        response = ClientEventsSubscribeResponse()
        response.ParseFromString(response_future.result().content)

        # Forked all the way back to genesis, restart with no known_ids
        if (response.status == ClientEventsSubscribeResponse.UNKNOWN_BLOCK
                and known_ids):
            self.start()

        if response.status != ClientEventsSubscribeResponse.OK:
            raise RuntimeError(
                'Subscription failed with status: {}'.format(
                    ClientEventsSubscribeResponse.Status.Name(
                        response.status)))

        self._is_active = True

        LOGGER.debug('Successfully subscribed to state delta events')
        while self._is_active:
            message_future = self._stream.receive()

            event_list = EventList()
            event_list.ParseFromString(message_future.result().content)
            for handler in self._event_handlers:
                handler(event_list.events)

    def stop(self):
        """Stops the Subscriber, unsubscribing from state delta events and
        closing the the stream's connection.
        """
        self._is_active = False

        LOGGER.debug('Unsubscribing from state delta events')
        request = ClientEventsUnsubscribeRequest()
        response_future = self._stream.send(
            Message.CLIENT_EVENTS_UNSUBSCRIBE_REQUEST,
            request.SerializeToString())
        response = ClientEventsUnsubscribeResponse()
        response.ParseFromString(response_future.result().content)

        if response.status != ClientEventsUnsubscribeResponse.OK:
            LOGGER.warning(
                'Failed to unsubscribe with status: %s',
                ClientEventsUnsubscribeResponse.Status.Name(response.status))

        self._stream.close()
