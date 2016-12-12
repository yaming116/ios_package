#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import argparse
import os
import subprocess

import bundle_file_copy as bundle_file
import launch_image_make
import update_config
import utils.utils as tools
from icon_make import make as icon_make

'a script for build ios package'

__author__ = 'sunshanming'


appIconFileName = 'AppIcon60x60@3x.png'
plist_key = 'plist'
header_key = 'header_file_key'
login_keychain = '~/Library/Keychains/login.keychain'


parser = argparse.ArgumentParser(description='a script for build ios package')
parser.add_argument('--password', dest='password', help='os password', required=True)
parser.add_argument('--source', dest='source', help='ios source path', required=True)
parser.add_argument('--config', dest='config', help='ios config path', required=True)
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Print verbose logging.')

args = parser.parse_args()

verbose = args.verbose or False
config = os.path.abspath(args.config)
source = os.path.abspath(args.source)
password = args.password

json_config_data = None

if verbose:
    print 'ios config path %s' % config
    print 'ios source path %s' % source


app_icon = os.path.join(config, 'AppIcon', 'AppIcon60x60@3x.png')
config_json = os.path.join(config, 'config.json')
launch_image_dir = os.path.join(config, 'LaunchImage')
image_resource = os.path.join(config, 'ImageResources')


resource = {config_json, app_icon}

app_icon_dist = os.path.join(source, 'URConfigFiles', 'Assets.xcassets', 'AppIcon.appiconset')
app_launch_image_dist = os.path.join(source, 'URConfigFiles', 'Assets.xcassets', 'LaunchImage.launchimage')

app_bundle_dist = os.path.join(source, 'URConfigFiles', 'URConfigResource.bundle')
app_image_folder_dist = os.path.join(app_bundle_dist, 'Images')

plist = os.path.join(source, 'URConfigFiles', 'info.plist')
# 头文件
config_header = os.path.join(source, 'URConfigFiles', 'URConfigHeader.h')


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
    # launch_image_make check
    launch_image_make.check_config(launch_image_dir)
    # check bundle image resource
    bundle_file.check(image_resource, verbose)

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


def add_p12_certification():

    if verbose:
        print 'start import p12'
        print '========================================='
        subprocess.check_call('security list-keychains' , shell=True)
    p12_file = json_config_data['p12_file_path']
    p12_pass = json_config_data['p12_password']
    if not os.path.exists(p12_file):
        raise ValueError('p12 file not exist')
    if not p12_pass or len(p12_pass) == 0:
        raise ValueError('p12 password is null')

    subprocess.check_call('security import %s -k %s -P %s -T /usr/bin/codesign' % (p12_file, login_keychain, p12_pass),  shell=True)


def open_provision_file():

    provision_file = json_config_data['provision_file_path']
    if verbose:
        print 'start import provision file'
        print 'provision_file path: %s' % provision_file

    if os.path.exists(provision_file):
        subprocess.check_call('open %s' % provision_file,  shell=True)
    else:
        print 'provision file not exist'


def main():
    has_error = False
    # unlock system
    try:
        subprocess.check_call('security unlock-keychain -p %s %s' % ( password, login_keychain), shell=True)
    except Exception as e:
        print 'unlock system error: %s' % e

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
        json_config_data = tools.load_json_from_file(config_json, verbose)
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
        print 'icon make exception: %s' % e
        has_error = True

    if has_error:
        return
    try:
        launch_image_make.copy(launch_image_dir, app_launch_image_dist, verbose)
    except Exception as e:
        print 'launch image exception: %s' % e

    if has_error:
        return
    try:
        bundle_file.copy(image_resource, app_image_folder_dist, verbose)
    except Exception as e:
        print 'bundle image copy exception: %s' % e
        has_error = True

    # update plist
    if has_error:
        return
    try:
        update_config.update_plist(json_config_data[plist_key], plist, verbose)
    except Exception as e:
        print 'update plist fail: %s' % e
        has_error = True

    # update header file
    if has_error:
        return
    try:
        update_config.update_header(json_config_data[header_key], config_header, verbose)
    except Exception as e:
        print 'update header file fail: %s' % e
        has_error = True

    if has_error:
        return
    try:
        add_p12_certification()
    except Exception as e:
        print 'add p12 certification exception: %s' % e
        has_error = True

    if has_error:
        return
    try:
        open_provision_file()
    except Exception as e:
        print 'open provision file exception: %s' % e
        has_error = True

if __name__ == '__main__':
    main()

