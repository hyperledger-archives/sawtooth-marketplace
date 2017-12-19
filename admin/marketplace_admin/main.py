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

import sys
import argparse
import logging

from marketplace_admin.commands import seed
from marketplace_admin.commands import renew
from marketplace_admin.commands import schedule


LOGGER = logging.getLogger(__name__)


def parse_args(args):
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('-v', '--verbose',
                        action='count',
                        default=0,
                        help='Increase level of output sent to stderr')

    parser = argparse.ArgumentParser(parents=[parent_parser])
    subparsers = parser.add_subparsers(title='subcommands', dest='command')
    subparsers.required = True

    seed.init_seed_parser(subparsers)
    renew.init_renew_parser(subparsers)
    schedule.init_schedule_parser(subparsers)

    return parser.parse_args(args)


def init_logger(level):
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    if level == 1:
        logger.setLevel(logging.INFO)
    elif level > 1:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARN)


def main():
    opts = parse_args(sys.argv[1:])
    init_logger(opts.verbose)

    if opts.command == 'seed':
        seed.do_seed(opts)
    elif opts.command == 'renew':
        renew.do_renew(opts)
    elif opts.command == 'schedule':
        schedule.do_schedule(opts)
    else:
        raise RuntimeError('Unrecognized command: {}'.format(opts.command))
