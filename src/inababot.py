#!/usr/bin/python
# inababot/src/inababot.py
#
# Copyright (C) 2011 - Reisen Udonge
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import logging
from optparse import OptionParser

from xmppbot import XmppBot

def main():
    optp = OptionParser()
    optp.add_option('-q', '--quiet', help='set logging to ERROR', action='store_const',
    dest='loglevel', const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG', action='store_const',
    dest='loglevel', const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM', action='store_const',
    dest='loglevel', const=5, default=logging.INFO)
    optp.add_option('-j', '--jid', dest='jid', help='JID, username@server.name/resource')
    optp.add_option('-p', '--password', dest='password', help='Пароль от аккаунта')
    optp.add_option('-o', '--owner', dest='owner', help='JID владельца')
    opts, args = optp.parse_args()
    logging.basicConfig(level=opts.loglevel, format='%(levelname)-8s %(message)s')
    bot = XmppBot(opts.jid, opts.password, opts.owner)
    bot.run()

if __name__ == '__main__' :
    main()
