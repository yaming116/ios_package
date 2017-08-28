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

            if not value or len(value) <= 0:
                print 'value is null'
                continue

            if test and key == u'CFBundleName':
                value = u'T-' + value

            command = "/usr/libexec/PlistBuddy -c 'Set :%s %s' %s" % (key, value, plist_path)
            if verbose:
                print 'command: %s' % command
            subprocess.check_call(command, shell=True)
        try:
            key = u'NSAppTransportSecurity:NSAllowsArbitraryLoads'
            if test:
                value = 1
            else:
                value = 0
            command = "/usr/libexec/PlistBuddy -c 'Set :%s %s' %s" % (key, value, plist_path)
            subprocess.check_call(command, shell=True)
            if verbose:
                print 'command: %s' % command
        except Exception as e1:

            pass

    except Exception as e:
        raise e


def update_plist_commit_id(commit_id, plist_path, verbose):
    try:
        key = u'CommitId'
        command = "/usr/libexec/PlistBuddy -c 'Set :%s %s' %s" % (key, commit_id, plist_path)
        subprocess.check_call(command, shell=True)
        if verbose:
            print 'command: %s' % command
    except Exception as e1:
        pass


def add_pay(update_json, plist_path, verbose):
    if verbose:
        print 'start update plist for pay'
    if not update_json:
        return
    print 'update json value: \n %s' % update_json

    try:
        '''
        /usr/libexec/PlistBuddy -c "Delete :CFBundleURLTypes"
        /usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes array" info.plist
        /usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes:0 dict" info.plist
        /usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes:0:CFBundleTypeRole string Editor" info.plist
        /usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes:0:CFBundleURLName string winxin" info.plist
        /usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes:0:CFBundleURLSchemes array" info.plist
        /usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes:0:CFBundleURLSchemes:0 string wxa5ae17722e3472ae" info.plist
        '''
        command = '/usr/libexec/PlistBuddy -c "Delete :CFBundleURLTypes" %s' % plist_path
        add_array = '/usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes array" %s '% plist_path
        add_dict = '/usr/libexec/PlistBuddy -c "Add  :CFBundleURLTypes:%s dict" %s '
        add_role = '/usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes:%s:CFBundleTypeRole string Editor" %s'
        add_url_name = '/usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes:%s:CFBundleURLName string %s" %s'
        add_url_scheme = '/usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes:%s:CFBundleURLSchemes array" %s'
        add_url_schemes = '/usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes:%s:CFBundleURLSchemes:0 string %s" %s'

        try:
            subprocess.check_call(command, shell=True)
        except Exception:
            # ignore ,some version code not contain CFBundleURLTypes
            print 'not found CFBundleURLTypes'
        if verbose:
            print 'command: %s' % command
        subprocess.check_call(add_array, shell=True)
        if verbose:
            print 'command: %s' % add_array
        index = 0
        for key, value in update_json.items():
            command = add_dict % (index, plist_path)
            subprocess.check_call(command, shell=True)
            if verbose:
                print 'command: %s' % command

            command = add_role % (index, plist_path)
            subprocess.check_call(command, shell=True)
            if verbose:
                print 'command: %s' % command

            command = add_url_name % (index, key,  plist_path)
            subprocess.check_call(command, shell=True)
            if verbose:
                print 'command: %s' % command

            command = add_url_scheme % (index, plist_path)
            subprocess.check_call(command, shell=True)
            if verbose:
                print 'command: %s' % command

            command = add_url_schemes % (index, value,  plist_path)
            subprocess.check_call(command, shell=True)
            if verbose:
                print 'command: %s' % command
            index += 1
    except Exception as e:
        print 'update plist for pay error'
        raise e


def update_bundle_id(bundle_id, plist_path, pbxpproj, verbose):
    try:
        update_plist_key('CFBundleIdentifier', bundle_id, plist_path ,verbose)
        update_pbxproj(pbxpproj, bundle_id, verbose)
    except Exception as e:
        print 'update bundle id error: %s' % e.message
        raise e


def update_plist_key(key, value, plist_path, verbose):
    command = "/usr/libexec/PlistBuddy -c 'Set :%s %s' %s" % (key, value, plist_path)
    if verbose:
        print 'command: %s' % command
    subprocess.check_call(command, shell=True)


def update_plist_option(options, plist_path, verbose):

    if not options:
        return
    if verbose:
        print 'update option plist config'
        print '=========================='
    if options.has('HEAD_IMG') and options['HEAD_IMG']:
        print 'has HEAD_IMG'
        update_plist_key('HomeTitleIcon', True, plist_path, verbose)
    else:
        print 'not found HEAD_IMG'
        update_plist_key('HomeTitleIcon', False, plist_path, verbose)


def update_pbxproj(path, bundle_id, verbose):
    try:
        if verbose:
            print 'start update projdec.pbxproj file'

        data = tools.load_data_from_file(path, verbose)

        # bundle id
        pattern = r'\bPRODUCT_BUNDLE_IDENTIFIER\b\s=\s[^"]{1}.*'
        value = 'PRODUCT_BUNDLE_IDENTIFIER = %s; ' % bundle_id
        data = re.sub(pattern, value , data)

        # change device family
        pattern = r'\bTARGETED_DEVICE_FAMILY\b\s=.*'
        value = 'TARGETED_DEVICE_FAMILY = 1; '
        data = re.sub(pattern, value, data)

        # change ProvisioningStyle 改成手动签名
        pattern = r'\bProvisioningStyle\b\s=.*'
        value = 'ProvisioningStyle = Manual; '
        data = re.sub(pattern, value, data)

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

            if not value or len(str(value)) <= 0:
                print 'value is null'
                continue

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

            else:
                if verbose:
                    print 'can not found header file key: %s' % header_key


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
    # update_plist(json['plist'], './temp/URConfigHeader.h', False,  False)
    # update_pbxproj('./temp/project.pbxproj', 'com.ucmed.rxp', True)
    update_header(json['header'], 'temp/TencentConfig.h', False, True)






