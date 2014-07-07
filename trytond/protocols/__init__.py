#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from http import HTTPDaemon
from jsonrpc import JSONRPCDaemon
from webdav import WebDAVServerThread
from xmlrpc import XMLRPCDaemon


PROTOCOLS = {
    'http': HTTPDaemon,
    'jsonrpc': JSONRPCDaemon,
    'webdav': WebDAVServerThread,
    'xmlrpc': XMLRPCDaemon,
}
