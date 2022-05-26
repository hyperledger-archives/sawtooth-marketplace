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

FROM ubuntu:16.04

RUN echo "deb apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8AA7AF1F1091A5FD" && \
    echo 'deb http://repo.sawtooth.me/ubuntu/1.0/stable xenial universe' >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --allow-unauthenticated -q python3-grpcio-tools=1.1.3-1 \
        python3-pip \
	python3-cffi \
        python3-sawtooth-sdk \
        python3-sawtooth-signing \
        python3-sawtooth-rest-api \
	curl

RUN pip3 install \
    uvloop==0.14 \
    bcrypt==3.1.5 \
    ujson==3.1.0 \
    itsdangerous==1.1.0 \
    rethinkdb \
    sanic==0.8.3 \
    pycrypto

WORKDIR /project/sawtooth-marketplace

ENV PATH $PATH:/project/sawtooth-marketplace/bin

EXPOSE 8000/tcp

CMD ["marketplace-rest-api"]
