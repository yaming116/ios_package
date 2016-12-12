#!/usr/bin/env python
# _*_ coding: utf-8 _*_

'update plist file and header file'


from plistlib import *
import re
import utils.utils as tools
import codecs
# try:
#     plist = readPlist("./temp/info.plist")
#
#     print plist
#     print plist['CFBundleDisplayName']
#     plist['CFBundleDisplayName'] = 'test'
#
#     writePlist(plist, "./temp/info.plist")
# except Exception, e:
#     print "Not a plist:", e


def update_plist(update_json, plist_path, verbose):
    if verbose:
        print 'start update plist'

    print 'update json value: \n %s' % update_json

    try:
        plist = readPlist(plist_path)

        for dic in update_json:

            plist_key = dic['plist_key']
            des = dic['des']
            value = dic['value']

            if verbose:
                print '%s %s=%s' % (des, plist_key, value)

            plist[plist_key] = value
        writePlist(plist, plist_path)
    except Exception as e:
        raise e


def update_header(header_json , header_path, verbose):
    try:
        if verbose:
            print 'start update header file'

        data = tools.load_data_from_file(header_path, verbose)

        pattern = r'\bdefine\b\s\b%s\b.*'
        value = r'define %s  %s'

        for header in header_json:
            header_key = header['header_key']
            header_value = header['value']

            data = re.sub(pattern % header_key, value % (header_key, header_value), data)

        with codecs.open(header_path, 'w', "utf-8") as header_file:
            header_file.write(data)

        if verbose:
            print 'header file result \n %s' % data

    except Exception as e:
        raise e


if __name__ == '__main__':
    json = tools.load_json_from_file('./temp/config.json', True)
    # update_header(json['header_file_key'], './temp/URConfigHeader.h', True)
    update_plist(json['plist'], './temp/info.plist', True)




