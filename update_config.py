#!/usr/bin/env python
# _*_ coding: utf-8 _*_

'update plist file and header file'


import subprocess
import re
import utils.utils as tools
import codecs
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
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


def update_plist(update_json, plist_path, verbose, test):
    if verbose:
        print 'start update plist'

    print 'update json value: \n %s' % update_json

    try:
        for key, value in update_json.items():

            if verbose:
                print 'plist: %s=%s' % (key, value)

            if test and key == 'CFBundleDisplayName':
                value = 'T-' + value

            command = "/usr/libexec/PlistBuddy -c 'Set :%s %s' %s" % (key, value, plist_path)
            if verbose:
                print 'command: %s' % command
            subprocess.check_call(command, shell=True)
    except Exception as e:
        raise e


def update_bundle_id(bundle_id, plist_path, pbxpproj, verbose):
    try:

        command = "/usr/libexec/PlistBuddy -c 'Set :%s %s' %s" % ('CFBundleIdentifier', bundle_id, plist_path)
        if verbose:
            print 'command: %s' % command
        subprocess.check_call(command, shell=True)

        update_pbxproj(pbxpproj, bundle_id, verbose)
    except Exception as e:
        print 'update bundle id error: %s' % e.message
        raise e


def update_pbxproj(path, bundle_id, verbose):
    try:
        if verbose:
            print 'start update projdec.pbxproj file'

        data = tools.load_data_from_file(path, verbose)

        pattern = r'\bPRODUCT_BUNDLE_IDENTIFIER\b\s=\s[^"]{1}.*'
        value = 'PRODUCT_BUNDLE_IDENTIFIER = %s; ' % bundle_id

        data = re.sub(pattern, value , data)

        with codecs.open(path, 'w', "utf-8") as header_file:
            header_file.write(data)

    except Exception as e:
        print 'update projdec.pbxproj error'
        raise e


def update_header(header_json , header_path, verbose):
    try:
        if verbose:
            print 'start update header file'

        data = tools.load_data_from_file(header_path, verbose)

        pattern = r'\bdefine\b\s\b%s\b.*'
        store_value = r'define %s  %s'

        for key, value in header_json.items():
            header_key = key
            header_value = value

            data = re.sub(pattern % header_key, store_value % (header_key, header_value), data)

        with codecs.open(header_path, 'w', "utf-8") as header_file:
            header_file.write(data)

        if verbose:
            print 'header file result \n %s' % data

    except Exception as e:
        raise e


if __name__ == '__main__':
    json = tools.load_json_from_file('./temp/config.json', True)
    update_header(json['header'], './temp/URConfigHeader.h', True)
    # update_pbxproj('./temp/project.pbxproj', 'com.ucmed.rxp', True)




