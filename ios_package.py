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


appIconFileName = 'AppIcon60x60@3x.png'
plist_key = 'plist'
header_key = 'header'
login_keychain = '~/Library/Keychains/login.keychain'


parser = argparse.ArgumentParser(description='a script for build ios package')
parser.add_argument('--source', dest='source', help='ios source path', required=True)
parser.add_argument('--password', dest='password', help='os password')
parser.add_argument('--name', dest='name', help='project name')
parser.add_argument('--config', dest='config', help='ios config path', required=True)
parser.add_argument('-test', '--test', dest='test', action='store_true' , help='test ipa build')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Print verbose logging.')

args = parser.parse_args()

verbose = args.verbose or False
test = args.test or False
parent_config = os.path.abspath(args.config)
source = os.path.abspath(args.source)
password = args.password
name = args.name

config = os.path.join(parent_config, 'URConfigFiles')

json_config_data = None
json_config_data_key = None
bundle_json_data = None
export_archive = None

if verbose:
    print 'ios parent config path %s' % parent_config
    print 'ios config path %s' % config
    print 'ios source path %s' % source


app_icon = os.path.join(config, 'AppIcon', 'AppIcon60x60@3x.png')
config_json = os.path.join(config, 'config.json')
launch_image_dir = os.path.join(config, 'LaunchImage')
image_resource = os.path.join(config, 'ImageResources')


resource = {config_json, app_icon}

app_icon_dist = os.path.join(source, 'URConfigFiles', 'Assets.xcassets', 'AppIcon.appiconset')
ipa_dist = os.path.join(config , 'IPA')
app_launch_image_dist = os.path.join(source, 'URConfigFiles', 'Assets.xcassets', 'LaunchImage.launchimage')

app_bundle_dist = os.path.join(source, 'URConfigFiles', 'URConfigResource.bundle')
app_image_folder_dist = os.path.join(app_bundle_dist, 'Images')

plist = os.path.join(source, 'URConfigFiles', 'Info.plist')
bundle_json = os.path.join(source, 'URConfigFiles', 'URConfigJSON.geojson')

# 头文件
config_header = os.path.join(source, 'URConfigFiles', 'URConfigHeader.h')

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
    # load bundle json data
    if os.path.exists(bundle_json):
        bundle_data = tools.load_json_from_file(bundle_json)
        global bundle_json_data
        bundle_json_data = bundle_data['coordinates']
    else:
        if verbose:
            print 'not found %s' % bundle_json
    # launch_image_make check
    launch_image_make.check_config(launch_image_dir)
    # check bundle image resource
    bundle_file.check(bundle_json_data, image_resource, verbose)

    #clean app icon
    if os.path.exists(app_icon_dist):
        for f in os.listdir(app_icon_dist):
            os.remove(os.path.join(app_icon_dist, f))
    else:
        os.makedirs(app_icon_dist)

    #clean app launch image
    if os.path.exists(app_launch_image_dist):
        for f in os.listdir(app_launch_image_dist):
            os.remove(os.path.join(app_launch_image_dist, f))
    else:
        os.makedirs(app_launch_image_dist)

    # clean bundle image
    if os.path.exists(app_image_folder_dist):
        for f in os.listdir(app_image_folder_dist):
            os.remove(os.path.join(app_image_folder_dist, f))
    else:
        os.makedirs(app_image_folder_dist)

    # create ipa dir
    if not os.path.exists(ipa_dist):
        os.makedirs(ipa_dist)


def pod_install():
    global name
    if not name:
        name = os.path.basename(source)
    xcworkspace = os.path.join(source, name)

    subprocess.check_call('cd %s && ls -al && pod install' % xcworkspace, shell=True)


def get_project_pbxpproj():
    pbxproj = os.path.join(source, name, '%s.xcodeproj' % name, 'project.pbxproj')
    if not os.path.exists(pbxproj):
        raise ValueError('project.pbxproj not found: %s' % pbxproj)
    return pbxproj


def add_p12_certification():

    if verbose:
        print 'start import p12'
        print '========================================='
        subprocess.check_call('security list-keychains' , shell=True)
    p12_file = json_config_data_key['UR_P12_FILE']
    p12_pass = json_config_data_key['UR_P12_PASSWORD']
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
    return get_args_from_provision_file('Name')


def get_team_name():
    return get_args_from_provision_file('TeamName')



'''
xcodebuild archive -workspace RubikU-Popular.xcworkspace -scheme  RubikU-Popular
-configuration Release -derivedDataPath ./build -archivePat h  ./build/Products/test.xcarchive
'''


def archive():
    uuid = check_dev().strip()
    xcworkspace = os.path.join(source, name, '%s.xcworkspace' % name)
    global export_archive
    export_archive = '%s/build/Products/%s.xcarchive ' % (config, name)

    if not test:
        distribution = 'iPhone Distribution: %s' % get_team_name()
    else:
        distribution = 'iPhone Developer: %s' % get_team_name()

    shutil.rmtree(os.path.join(config, 'build'), True)
    command = 'xcodebuild clean archive -workspace %s -scheme  %s -configuration Release ' \
              '-derivedDataPath %s/build -archivePath %s  ' \
              'CODE_SIGN_IDENTITY="%s"' \
              ' PROVISIONING_PROFILE=%s | xcpretty' % (xcworkspace, name, config, export_archive, distribution, uuid)
    if verbose:
        print 'build xcworkspace: %s' % xcworkspace
        print 'build command: %s' % command
    subprocess.check_call(command, shell=True)


def export_ipa():
    name = get_provisioning_profile().strip()
    localtime = time.localtime(time.time())
    day = time.strftime("%Y-%m-%d", time.localtime())
    id = int(time.mktime(localtime) / 10)
    ipa_name = '%s_%s.ipa' % (day, id)
    p = os.path.join(ipa_dist, ipa_name)
    command = 'xcodebuild -exportArchive -exportFormat IPA -archivePath %s -exportPath %s -exportProvisioningProfile %s'\
              % (export_archive, p, name)

    if verbose:
        print 'command: %s' % command
    subprocess.check_call(command, shell=True)

    print '========================================'
    print 'app_path: %s' % p
    print '========================================'


def main():
    has_error = False
    # unlock system
    try:
        subprocess.check_call('security unlock-keychain -p %s %s' % ( password, login_keychain), shell=True)
    except Exception as e:
        print 'unlock system error: %s' % e
        has_error = True

    if has_error:
        return
    if verbose:
        print 'unlock system ok'

    if not os.path.isdir(source):
        print '%s is not an existing directory' % source
        return

    if not os.path.isdir(config):
        print '%s is not an existing directory' % config
        return

    try:
        global json_config_data
        global json_config_data_key
        json_config_data = tools.load_json_from_file(config_json, verbose)
        if test:
            json_config_data_key = json_config_data['key_test']
        else:
            json_config_data_key = json_config_data['key']
    except Exception as e:
        print 'load json config fail: %s' % e
        has_error = True

    if has_error:
        return

    try:
        check_config()
    except Exception as e:
        print e;
        has_error = True

    if has_error:
        return
    try:
        icon_make(verbose, app_icon, app_icon_dist)
    except Exception as e:
        print 'icon make exception: %s' % e.message
        has_error = True

    if has_error:
        return
    try:
        launch_image_make.copy(launch_image_dir, app_launch_image_dist, verbose)
    except Exception as e:
        print 'launch image exception: %s' % e.message

    if has_error:
        return
    try:
        bundle_file.copy(bundle_json_data, image_resource, app_image_folder_dist, verbose)
    except Exception as e:
        print 'bundle image copy exception: %s' % e.message
        has_error = True

    # pod install
    if has_error:
        return
    try:
        pod_install()
    except Exception as e:
        print 'pod install exception: %s' % e.message
        has_error = True

    # update plist
    if has_error:
        return
    try:
        update_config.update_plist(json_config_data[plist_key], plist, verbose, test)
    except Exception as e:
        print 'update plist fail: %s' % e
        has_error = True

    # update bundle id

    if has_error:
        return
    try:
        update_config.update_bundle_id(json_config_data_key['UR_BUNDLE_IDENTIFIER'], plist, get_project_pbxpproj(),
                                       verbose)
    except Exception as e:
        print 'update plist fail: %s' % e
        has_error = True

    # update header file
    if has_error:
        return
    try:
        update_config.update_header(json_config_data[header_key], config_header, verbose)
    except Exception as e:
        print 'update header file fail: %s' % e.message
        has_error = True

    if has_error:
        return

    try:
        add_p12_certification()
    except Exception as e:
        print 'add p12 certification exception: %s' % e.message
        has_error = True

    if has_error:
        return
    try:
        open_provision_file()
    except Exception as e:
        print 'open provision file exception: %s' % e.message
        has_error = True

    if has_error:
        return
    try:
        archive()
    except Exception as e:
        print 'archive exception: %s' % e.message
        has_error = True

    if has_error:
        return
    try:
        export_ipa()
    except Exception as e:
        print 'export ipa exception: %s' % e.message


if __name__ == '__main__':
    main()

