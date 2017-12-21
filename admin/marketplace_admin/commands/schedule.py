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

import re
import logging
import subprocess
from os import path
from marketplace_admin.services import api
from marketplace_admin.services import data


LOGGER = logging.getLogger(__name__)


def init_schedule_parser(subparsers):
    parser = subparsers.add_parser(
        'schedule',
        help='Uses cron to regularly call another mktadm command')
    parser.add_argument(
        '-H', '--hourly',
        action='store_true',
        help='Call the command every hour')
    parser.add_argument(
        '-D', '--daily',
        action='store_true',
        help='Call the command every day')
    parser.add_argument(
        '-W', '--weekly',
        action='store_true',
        help='Call the command once a week')
    parser.add_argument(
        '-M', '--monthly',
        action='store_true',
        help='Call the command once a month')
    parser.add_argument(
        '-r', '--remove',
        action='store_true',
        help='Removes the specified command from the schedule')
    parser.add_argument(
        'schedule_command',
        type=str,
        help='The mktadm command to schedule')

    return parser


def do_schedule(opts):
    command = _get_command(opts)

    try:
        crontab = subprocess.check_output(['crontab', '-l'],
                                          stderr=subprocess.PIPE).decode()
    except subprocess.CalledProcessError:
        crontab = ''

    if opts.remove:
        cron_line = ''
    else:
        cron_line = '{} {}'.format(_get_schedule(opts), command)

    if re.search(command, crontab):
        new_crontab = re.sub('^.*{}$'.format(command),
                             cron_line,
                             crontab,
                             flags=re.MULTILINE)[:-1]
    else:
        new_crontab = crontab + cron_line

    subprocess.call('echo "{}" | crontab -'.format(new_crontab), shell=True)


def _get_schedule(opts):
    if opts.hourly:
        return '0 * * * *'
    if opts.daily:
        return '0 0 * * *'
    if opts.weekly:
        return '0 0 * * 0'
    if opts.monthly:
        return '0 0 1 * *'
    raise RuntimeError('No schedule specified, must specify --hourly, '
                       '--daily, --weekly, or --monthly')

def _get_command(opts):
    cmd_rel = '../../../bin/mktadm'
    cmd_abs = path.realpath(path.join(path.dirname(__file__), cmd_rel))
    return '{} {}'.format(cmd_abs, opts.schedule_command)
