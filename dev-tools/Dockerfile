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

# This Dockerfile is for running protogen, lint, and unit-tests

FROM ubuntu:xenial

RUN apt-get update && apt-get install -yq python3-pip

RUN pip3 install pylint==1.7.4 pycodestyle==2.3.1 grpcio-tools==1.7.0 nose2==0.7.2

WORKDIR /project/sawtooth-marketplace

CMD ['./bin/protogen']
