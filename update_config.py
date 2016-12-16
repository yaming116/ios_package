#!/usr/bin/env python
# _*_ coding: utf-8 _*_

'update plist file and header file'


import subprocess
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


def update_plist(update_json, plist_path, pbxpproj, verbose, test):
    if verbose:
        print 'start update plist'

    print 'update json value: \n %s' % update_json

    try:
        for dic in update_json:

            plist_key = dic['plist_key']
            des = dic['des']
            value = dic['value']

            if verbose:
                print '%s %s=%s' % (des, plist_key, value)

            if test and plist_key == 'CFBundleDisplayName':
                value = 'T-' + value

            if plist_key == 'CFBundleIdentifier':
                update_pbxproj(pbxpproj, value, verbose)

            command = "/usr/libexec/PlistBuddy -c 'Set :%s %s' %s" % (plist_key, value, plist_path)
            if verbose:
                print 'command: %s' % command
            subprocess.check_call(command, shell=True)
    except Exception as e:
        raise e


def update_pbxproj(path, bundle_id, verbose):
    try:
        if verbose:
            print 'start update projdec.pbxproj file'

        data = tools.load_data_from_file('', verbose)

        pattern = r'\bPRODUCT_BUNDLE_IDENTIFIER\b\s=\s[^"]{1}.*'
        value = r'bPRODUCT_BUNDLE_IDENTIFIER = %s; ' % bundle_id

        data = re.sub(pattern , value % bundle_id, data)

        with codecs.open(path, 'w', "utf-8") as header_file:
            header_file.write(data)

        if verbose:
            print 'projdec.pbxproj file result \n %s' % data

    except Exception as e:
        print 'update projdec.pbxproj error'
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
    json = tools.load_json_from_file('../resource/config.json', True)
    # update_header(json['header_file_key'], './temp/URConfigHeader.h', True)
    update_plist(json['plist'], '../resource/info.plist', True, False)




