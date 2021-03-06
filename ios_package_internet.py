#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import argparse
import os
import subprocess
import time

import bundle_file_copy as bundle_file
import launch_image_make
import update_config
import utils.utils as tools
from icon_make import make as icon_make
import shutil

'a script for build ios package'

__author__ = 'sunshanming'
__version__ = '1.0.1'


appIconFileName = 'AppIcon60x60@3x.png'
plist_key = 'plist'
header_key = 'header'
pay = 'pay'
login_keychain = '~/Library/Keychains/login.keychain'
ExportOptions_PATH = '/Volumes/BAK/build/ExportOptions_enterprise_internet.plist'


parser = argparse.ArgumentParser(description='a script for build ios package')
parser.add_argument('--source', dest='source', help='ios source path', required=True)
parser.add_argument('--password', dest='password', help='os password')
parser.add_argument('--name', dest='name', help='project name')
parser.add_argument('--config', dest='config', help='ios config path', required=True)
parser.add_argument('-test', '--test', dest='test', action='store_true' , help='test ipa build')
parser.add_argument('-doctor', '--doctor', dest='doctor', action='store_true' , help='doctor or patient')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Print verbose logging.')

args = parser.parse_args()

verbose = args.verbose or False
test = args.test or False
doctor = args.doctor or False
parent_config = os.path.abspath(args.config)
source = os.path.abspath(args.source)
password = args.password
name = args.name
basename = os.path.basename(source)
export_option_path = os.path.abspath(ExportOptions_PATH)

config = os.path.join(parent_config, 'URPConfigFiles')

json_config_data = None
json_config_data_key = None
bundle_json_data = None
export_archive = None

if verbose:
    print 'ios parent config path %s' % parent_config
    print 'ios config path %s' % config
    print 'ios source path %s' % source
    print 'version is: %s' % __version__


app_icon = os.path.join(config, 'AppIcon', 'AppIcon60x60@3x.png')
app_icon_1024 = os.path.join(config, 'AppIcon', 'AppIcon1024x1024.png')
launch_image_dir = os.path.join(config, 'LaunchImage')
config_json = os.path.join(config, 'config.json')
image_resource = os.path.join(config, 'ImageResources')


resource = {config_json}

app_icon_dist = os.path.join(source, 'InternetHospital', 'Assets.xcassets', 'AppIcon.appiconset')
ipa_dist = os.path.join(parent_config , 'IPA')
app_launch_image_dist = os.path.join(source, 'InternetHospital', 'Assets.xcassets', 'LaunchImage.launchimage')

plist = os.path.join(source, 'InternetHospital', 'Info.plist')
bundle_json = os.path.join(source, 'InternetHospital', 'URConfigJSON.geojson')

# 头文件
config_header = os.path.join(source, 'InternetHospital','UI',  'TencentConfig.h')

if password is None or not len(password) > 0:
    password = os.getenv('os_password')

    if password is None or not len(password) > 0:
        raise ValueError('password is null')


def check_config():
    if verbose:
        print 'start check config'

    # check resourde
    for p in resource:
        if not os.path.exists(p):
            raise ValueError('%s not exists' % p)
        else:
            if verbose:
                print 'config: %s' % p

    # check bundle image resource
    # bundle_file.check(bundle_json_data, image_resource, verbose)

    #clean app icon
    if os.path.exists(app_icon_dist):
        for f in os.listdir(app_icon_dist):
            os.remove(os.path.join(app_icon_dist, f))
        pass
    else:
        os.makedirs(app_icon_dist)

    #clean app launch image
    if os.path.exists(app_launch_image_dist):
        for f in os.listdir(app_launch_image_dist):
            os.remove(os.path.join(app_launch_image_dist, f))
        pass
    else:
        os.makedirs(app_launch_image_dist)

    # create ipa dir
    if not os.path.exists(ipa_dist):
        os.makedirs(ipa_dist)


def pod_install():
    global name
    # if not name:
    #     name = os.path.basename(source)
    # xcworkspace = os.path.join(source, name)

    subprocess.check_call('cd %s && ls -al && pod deintegrate && pod update' % source, shell=True)


def get_project_pbxpproj():
    pbxproj = os.path.join(source, '%s.xcodeproj' % name, 'project.pbxproj')
    if not os.path.exists(pbxproj):
        raise ValueError('project.pbxproj not found: %s' % pbxproj)
    return pbxproj


def add_p12_certification():

    if verbose:
        print 'start import p12'
        print '========================================='
        subprocess.check_call('security list-keychains' , shell=True)
    p12_file = json_config_data_key.get('UR_P12_FILE', '')
    p12_pass = json_config_data_key.get('UR_P12_PASSWORD', '')
    if not os.path.exists(p12_file):
        print 'p12 file not exist'
        return
    if not p12_pass or len(p12_pass) == 0:
        raise ValueError('p12 password is null')

    subprocess.check_call('security import %s -k %s -P %s -T /usr/bin/codesign' % (p12_file, login_keychain, p12_pass),  shell=True)


def open_provision_file():

    provision_file = json_config_data_key['UR_MOBILE_PROVISION_FILE']
    if verbose:
        print 'start import provision file'
        print 'provision_file path: %s' % provision_file

    if os.path.exists(provision_file):
        subprocess.check_call('open %s' % provision_file,  shell=True)
    else:
        raise ValueError('provision file not exist')


def get_args_from_provision_file(key):
    provision_file = json_config_data_key['UR_MOBILE_PROVISION_FILE']
    command = '/usr/libexec/PlistBuddy -c "Print %s" /dev/stdin <<< $(/usr/bin/security cms -D -i %s)' % (key, provision_file)
    return subprocess.check_output(command, shell=True)


def check_dev():
    return get_args_from_provision_file('UUID')


def get_provisioning_profile():
    return get_args_from_provision_file('Name').strip()


def get_app_method():
    name = get_provisioning_profile()
    if 'AD' in name  or 'Ad_Hoc' in name:
        return 'ad-hoc'
    if 'Universal' in name:
        return 'enterprise'
    if 'Distribution' in name  or 'Dis' in name:
        return 'app-store'
    raise ValueError("证书命名出错，请包含 AD or Universal or Distribution")


def get_team_name():
    # env = get_args_from_provision_file('Entitlements:aps-environment').strip()
    env = 'product'
    team_name = get_args_from_provision_file('TeamName').strip()
    if 'development' == env:
        return 'iPhone Developer: %s' % team_name
    else:
        return 'iPhone Distribution: %s' % team_name


def get_team_identifier():
    return get_args_from_provision_file('Entitlements:com.apple.developer.team-identifier').strip()


'''
xcodebuild archive -workspace RubikU-Popular.xcworkspace -scheme  RubikU-Popular
-configuration Release -derivedDataPath ./build -archivePat h  ./build/Products/test.xcarchive
'''


def archive():
    uuid = check_dev().strip()
    xcworkspace = os.path.join(source, '%s.xcworkspace' % name)
    global export_archive
    export_archive = '%s/build/Products/%s.xcarchive ' % (parent_config, name)

    distribution =  get_team_name()

    shutil.rmtree(os.path.join(parent_config, 'build'), True)
    command = 'xcodebuild clean archive -workspace %s -scheme  %s -configuration Release ' \
              '-derivedDataPath %s/build -archivePath %s  ' \
              'PROVISIONING_PROFILE_SPECIFIER=%s DEVELOPMENT_TEAM=%s | xcpretty' % \
              (xcworkspace, name, parent_config, export_archive, get_provisioning_profile(),
               get_team_identifier())
    if verbose:
        print 'build xcworkspace: %s' % xcworkspace
        print 'build command: %s' % command
    subprocess.check_call(command, shell=True)


def export_ipa():
    localtime = time.localtime(time.time())
    day = time.strftime("%Y-%m-%d_%H:%M", time.localtime())
    id = int(time.mktime(localtime) / 10)
    ipa_name = '%s_%s_%s' % (day, id, basename)
    p = os.path.join(ipa_dist, ipa_name)
    command = 'xcodebuild -exportArchive -archivePath %s -exportPath %s -exportOptionsPlist %s' \
              % (export_archive, p, export_option_path)

    if verbose:
        print 'command: %s' % command
    subprocess.check_call(command, shell=True)

    for x in os.listdir(p):
        if os.path.splitext(x)[1] == '.ipa':
            print '========================================'
            print 'app_path: %s' % os.path.join(p, x)
            print '========================================'


def tran_key_json(json_data, key):
    path = json_data[key]
    result = tools.load_json_from_file(path, verbose)
    if verbose:
        print 'key data: %s' % result
    return result


def main():
    has_error = False
    # unlock system
    # ~/Library/Keychains/login.keychain
    try:
        subprocess.check_call('security unlock-keychain -p %s %s' % ( password, login_keychain), shell=True)
    except Exception as e:
        print 'unlock system error: %s' % e
        raise e
    if verbose:
        print 'unlock system ok'

    if not os.path.isdir(source):
        print '%s is not an existing directory' % source
        raise ValueError('%s is not an existing directory' % source)

    if not os.path.isdir(config):
        print '%s is not an existing directory' % config
        raise ValueError('%s is not an existing directory' % config)

    try:
        check_config()
    except Exception as e:
        print e
        raise e

    try:
        global json_config_data
        global json_config_data_key
        json_config_data = tools.load_json_from_file(config_json, verbose)
        if test:
            json_config_data_key = tran_key_json(json_config_data['key_test'], 'key_test')
        else:
            json_config_data_key = tran_key_json(json_config_data['key'], 'key')
    except Exception as e:
        print 'load json config fail: %s' % e
        print '加载证书失败,请检查相关配置'
        raise e

    try:
        if os.path.exists(app_icon):
            for f in os.listdir(app_icon_dist):
                os.remove(os.path.join(app_icon_dist, f))
            icon_make(verbose, app_icon, app_icon_1024, app_icon_dist)
        else:
            print '没有发现icon'
    except Exception as e:
        print 'icon make exception: %s' % e.message
        raise e

    try:
        launch_image_make.copy(launch_image_dir, app_launch_image_dist, verbose=verbose, inter=True)
    except Exception as e:
        print 'launch image exception: %s' % e.message

    # pod install
    try:
        pod_install()
    except Exception as e:
        print 'pod install exception: %s' % e.message
        raise e

    # update plist
    try:
        update_config.update_plist(json_config_data[plist_key], plist, verbose, test)
    except Exception as e:
        print 'update plist fail: %s' % e
        raise e

    # update plist for pay
    try:
        update_config.add_pay(json_config_data.get(pay), plist, verbose)
    except Exception as e:
        print 'update plist for pay fail: %s' % e
        raise e
    # update bundle id


    try:
        update_config.update_bundle_id(json_config_data_key['UR_BUNDLE_IDENTIFIER'], plist, get_project_pbxpproj(),
                                       verbose)
        update_config.update_pbxproj(get_project_pbxpproj(), json_config_data_key['UR_BUNDLE_IDENTIFIER'],
                                     get_team_identifier(),
                                     get_provisioning_profile(), check_dev(), verbose)
    except Exception as e:
        print 'update plist fail: %s' % e
        raise e

    # update header file
    try:
        if doctor:
            json_config_data[header_key]['EditionType'] = 2
        else:
            json_config_data[header_key]['EditionType'] = 1
        update_config.update_header(json_config_data[header_key], config_header, test, verbose)
    except Exception as e:
        print 'update header file fail: %s' % e.message
        raise e

    try:
        add_p12_certification()
    except Exception as e:
        print 'add p12 certification exception: %s' % e.message
        raise e


    try:
        open_provision_file()
    except Exception as e:
        print 'open provision file exception: %s' % e.message
        raise e

    try:
        archive()
    except Exception as e:
        print 'archive exception: %s' % e.message
        raise e

    try:
        update_config.update_export_options_plist(get_app_method(), json_config_data_key['UR_BUNDLE_IDENTIFIER'], get_provisioning_profile(), get_team_identifier(), export_option_path)
    except Exception as e:
        print 'update_export_options_plist exception: %s' % e.message
        raise e

    try:
        export_ipa()
    except Exception as e:
        print 'export ipa exception: %s' % e.message
        raise e


if __name__ == '__main__':
    main()

