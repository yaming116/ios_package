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

config = [{'idiom': 'iphone', 'subtype': '736h', 'filename': '1242-2208.png', 'minimum-system-version': '8.0', 'scale': '3x'},
          {'idiom': 'iphone', 'subtype': '667h', 'filename': '750-1334.png', 'minimum-system-version': '8.0', 'scale': '2x'},
          {'idiom': 'iphone', 'filename': '640-960.png', 'minimum-system-version': '7.0', 'scale': '2x'},
          {'idiom': 'iphone', 'subtype': 'retina4', 'filename': '640-1136.png', 'minimum-system-version': '7.0', 'scale': '2x'},
          {'idiom': 'ipad', 'filename': '768-1024.png', 'minimum-system-version': '7.0', 'scale': '1x'},
          {'idiom': 'ipad', 'filename': '1536-2048.png', 'minimum-system-version': '7.0', 'scale': '2x'}]


def check_config(launch_image_dir):

    for launch in config:
        p = path.join(launch_image_dir, launch['filename'])
        if not (path.exists(p)):
            raise ValueError('launch image not exist: %s' % p)


def copy(launch_image_dir, app_launch_image_dist, verbose=False):
    if verbose:
        print 'start launch image make'
    images = []
    for launch in config:
        p = path.join(launch_image_dir, launch['filename'])
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