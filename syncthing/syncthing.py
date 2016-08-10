#! /usr/bin/env python
# -*- coding: utf-8 -*-
# >>
#     python-syncthing, 2016
# <<

import os
import time
import logging
import warnings


logger = logging.getLogger('syncthing')


MINIMUM_TIMEOUT_SECS = 1.0


class Interface(object):
    def __init__(self, api_key, host='localhost', port=8384, timeout=5.0, is_https=False, ssl_cert=None):
        """ Connection management to the backend Syncthing API server.

            Args:
                api_key (str):
                    The authentication key used to communicate with Syncthing.
                    This is supplied via deferred instantiation in :meth:`.Syncthing.init`.
                host (str)
                port (int)
                timeout (float)
                is_https (bool)
                ssl_cert (str):
                    Path to a valid SSL certificate file.

        """

        self._api_key   = api_key
        self._host      = host
        self._is_https  = is_https
        self._port      = port
        self._ssl_cert  = ssl_cert
        self._timeout   = max(MINIMUM_TIMEOUT_SECS, float(timeout))

        if self._ssl_cert:
            assert os.path.exists(self._ssl_cert), 'File `%s` does not exist' % self._ssl_cert

        if self._is_https and not self._ssl_cert:
            warnings.warn('Using HTTPS without a specified `ssl_cert` file')

        # are we going to verify the calls/checks
        self.verify = True if self._ssl_cert else False

        # headers that need to be sent to Syncthing
        self._headers = dict()

        self.add_header('X-API-Key', self._api_key)

        # for caching
        self.last_req = None
        self.last_req_time = 0

    @property
    def connected(self):
        return self.is_connected()

    @property
    def headers(self):
        ret = dict()
        for key, value in self._headers.items():
            ret[key] = '\n'.join(value)
        return ret

    @property
    def host(self):
        return '%s://%s:%d' % (self.protocol, self._host, self._port)

    @property
    def options(self):
        return {
            'api_key': self._api_key,
            'host': self._host,
            'is_https': self._is_https,
            'port': self._port,
            'ssl_cert': self._ssl_cert,
            'timeout': self._timeout}

    @property
    def protocol(self):
        return 'https' if self._is_https else 'http'

    def add_header(self, key, value):
        values = self._headers.setdefault(key, list())
        values.append(value)

    def is_connected(self):
        pass

    def remove_header(self, key):
        self._headers.pop(key, None)


class Syncthing(object):
    def __init__(self, api_key=None, **kwargs):
        self._interface = None
        self._api_key = None

        if api_key:
            self.init(api_key, **kwargs)

    @property
    def api_key(self):
        return self._api_key

    @property
    def interface(self):
        return self._interface

    def init(self, api_key, **kwargs):
        """ Deferred instantiation to connect to the Syncthing API server.

            Args:
                api_key (str):
                    The authentication key used to communicate with a Syncthing
                    instance running on a local, or remote, machine.
        """
        if self._interface is not None:
            raise UserWarning('Cannot instantiate multiple interfaces to one connection')

        self._api_key = api_key
        self._interface = Interface(self.api_key, **kwargs)

    @classmethod
    def valid_api_key(cls, s):
        pass