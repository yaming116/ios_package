#!/usr/bin/env python
# _*_ coding: utf-8 _*_

'''
create app launch image

{   "extent" : "full-screen",
    "idiom" : "iphone",
    "subtype" : "retina4"
    "filename" : "640-1136.png"
    "minimum-system-version" : "7.0"
    "orientation" : "portrait"
    "scale" : "2x"
}
'''

import os.path as path
import json
import shutil
import os

config = [{'idiom': 'iphone', 'subtype': '736h', 'filename': '1242-2208.png', 'minimum-system-version': '8.0', 'scale': '3x'},
          {'idiom': 'iphone', 'subtype': '667h', 'filename': '750-1334.png', 'minimum-system-version': '8.0', 'scale': '2x'},
          {'idiom': 'iphone', 'filename': '640-960.png', 'minimum-system-version': '7.0', 'scale': '2x'},
          {'idiom': 'iphone', 'subtype': 'retina4', 'filename': '640-1136.png', 'minimum-system-version': '7.0', 'scale': '2x'},
          {'idiom': 'ipad', 'filename': '768-1024.png', 'minimum-system-version': '7.0', 'scale': '1x'},
          {'idiom': 'ipad', 'filename': '1536-2048.png', 'minimum-system-version': '7.0', 'scale': '2x'}]

option = [{{'idiom': 'iphone', 'subtype': '243636h', 'filename': '1125-2436.png', 'minimum-system-version': '11.0', 'scale': '3x'}}
          ]

config_inter = [
    {'idiom': 'iphone', 'subtype': '736h', 'filename': '1242-2208.png', 'minimum-system-version': '8.0', 'scale': '3x'},
    {'idiom': 'iphone', 'subtype': '667h', 'filename': '750-1334.png', 'minimum-system-version': '8.0', 'scale': '2x'},
    {'idiom': 'iphone', 'filename': '640-960.png', 'minimum-system-version': '7.0', 'scale': '2x'},
    {'idiom': 'iphone', 'subtype': 'retina4', 'filename': '640-1136.png', 'minimum-system-version': '7.0',
     'scale': '2x'}];

config_default = [
    {"orientation" : "portrait","idiom" : "iphone","extent" : "full-screen","scale" : "1x"},
    {"orientation" : "landscape","idiom" : "iphone", "extent" : "full-screen","minimum-system-version":"8.0","subtype": "736h","scale" : "3x"}]


def check_config(launch_image_dir, inter=False):
    c = config
    if inter:
        c = config_inter
    for launch in c:
        p = path.join(launch_image_dir, launch['filename'])
        if not (path.exists(p)):
            raise ValueError('launch image not exist: %s' % p)


def copy(launch_image_dir, app_launch_image_dist, verbose=False, inter=False):
    if verbose:
        print 'start launch image make'
    images = []
    c = config
    if inter:
        c = config_inter
        images.extend(config_default)
    for launch in c:
        p = path.join(launch_image_dir, launch['filename'])
        shutil.copy(p, app_launch_image_dist)
        launch['extent'] = 'full-screen'
        launch['orientation'] = 'portrait'
        images.append(launch)

    for launch in option:
        p = path.join(launch_image_dir, launch['filename'])
        if os.path.exists(p) :
            shutil.copy(p, app_launch_image_dist)
            launch['extent'] = 'full-screen'
            launch['orientation'] = 'portrait'
            images.append(launch)

    content = {'images': images, 'info': {'version': 1, 'author': 'xcode'}}
    json_content = json.dumps(content, indent=1)

    if verbose:
        print "image json content: %s" % json_content
    with open(path.join(app_launch_image_dist, 'Contents.json'), mode='w') as icon_content:
        icon_content.write(json_content)