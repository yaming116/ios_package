#!/usr/bin/env python
# _*_ coding: utf-8 _*_

'a utils file'

import json


def load_json_from_file(path, verbose=False):
    if verbose:
        print 'load json file: %s' % path
    with open(path) as json_file:
        data = json.load(json_file)
        return data


def load_data_from_file(path, verbose=False):
    if verbose:
        print 'load file: %s' % path

    with open(path) as data_file:
        return data_file.read().decode('utf-8')