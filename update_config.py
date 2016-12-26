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

    displayName = update_json.get('CFBundleDisplayName')

    if not displayName:
        update_json['CFBundleDisplayName'] = update_json.get('CFBundleName')

    try:
        for key, value in update_json.items():

            if verbose:
                print 'plist: %s=%s' % (key, value)

            if test and key == u'CFBundleName':
                value = u'T-' + value

            command = "/usr/libexec/PlistBuddy -c 'Set :%s %s' %s" % (key, value, plist_path)
            if verbose:
                print 'command: %s' % command
            subprocess.check_call(command, shell=True)
        try:
            key = u'NSAppTransportSecurity:NSAllowsArbitraryLoads'
            if test:
                value = u'1'
            else:
                value = u'0'
            command = "/usr/libexec/PlistBuddy -c 'Set :%s %s' %s" % (key, value, plist_path)
            if verbose:
                print 'command: %s' % command
        except Exception as e1:
            pass

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


def update_header(header_json , header_path, test, verbose):
    try:
        if verbose:
            print 'start update header file'

        data = tools.load_data_from_file(header_path, verbose)

        pattern = r'\bdefine\b\s\b%s\b.*'
        store_string_value = r'define %s @"%s"'
        store_value = r'define %s %s'
        store_object_value = r'define %s  @%s'

        for key, value in header_json.items():
            header_key = key
            header_value = value

            match = re.search(pattern % header_key, data)

            if match:
                result = match.group().split(' ')
                v = result[-1]

                if v.startswith('@"'):
                    pattern_value = store_string_value
                    print 'start @:'
                elif v.startswith('@'):
                    pattern_value = store_object_value
                    print 'start @'
                else:
                    pattern_value = store_value
                    print 'not found'

            data = re.sub(pattern % header_key, pattern_value % (header_key, header_value), data)

        http_path = header_json.get('TEST_UR_HTTPURL', None)
        if test:
            if http_path and len(http_path) > 0:
                key = u'UR_HTTPURL'
                value = http_path
                data = re.sub(pattern % key, store_string_value % (key, value), data)
            else:
                raise ValueError('test http path not found')

        with codecs.open(header_path, 'w', "utf-8") as header_file:
            header_file.write(data)

        if verbose:
            print 'header file update success '

    except Exception as e:
        raise e


if __name__ == '__main__':
    json = tools.load_json_from_file('./temp/config.json', True)
    update_header(json['header'], './temp/URConfigHeader.h', False,  False)
    # update_pbxproj('./temp/project.pbxproj', 'com.ucmed.rxp', True)




