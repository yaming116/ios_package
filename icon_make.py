#!/usr/bin/env python
# _*_ coding: utf-8 _*_

'create app icon'

import json
import os
import subprocess

ICON_NAME = 'icon_%sx%s.png'

ico_list = [{'size': 20, 'multiple': 2, 'type': 'iphone'},
            {'size': 20, 'multiple': 3, 'type': 'iphone'},
            {'size': 29, 'multiple': 2, 'type': 'iphone'},
            {'size': 29, 'multiple': 3, 'type': 'iphone'},
            {'size': 40, 'multiple': 2, 'type': 'iphone'},
            {'size': 40, 'multiple': 3, 'type': 'iphone'},
            {'size': 60, 'multiple': 2, 'type': 'iphone'},
            {'size': 60, 'multiple': 3, 'type': 'iphone'},
            {'size': 20, 'multiple': 1, 'type': 'ipad'},
            {'size': 20, 'multiple': 2, 'type': 'ipad'},
            {'size': 29, 'multiple': 1, 'type': 'ipad'},
            {'size': 29, 'multiple': 2, 'type': 'ipad'},
            {'size': 40, 'multiple': 1, 'type': 'ipad'},
            {'size': 40, 'multiple': 2, 'type': 'ipad'},
            {'size': 76, 'multiple': 1, 'type': 'ipad'},
            {'size': 76, 'multiple': 2, 'type': 'ipad'},
            {'size': 83.5, 'multiple': 2, 'type': 'ipad'}]

HEAD_ICO = '医院logo@%sx.png'
head_list = [{'size': 20, 'multiple': 1},
             {'size': 20, 'multiple': 2},
             {'size': 20, 'multiple': 3}, ]


def make(verbose, app_icon, app_icon_dist):
    if verbose:
        print 'start icon make'
    if not os.path.exists(app_icon) :
        print 'app icon not found'
        return
    images = []
    for icon in ico_list:
        s = icon['size']
        multiple = icon['multiple']
        type = icon['type']
        size = int(s * multiple)

        icon_name = ICON_NAME % (size, size)

        images.append({'size': ('%sx%s' % (s, s)), 'idiom': type, 'filename': icon_name, 'scale': ('%sx' % multiple)})

        command = 'convert -resize %sx%s  %s  %s' % (
            size, size, app_icon, os.path.join(app_icon_dist, icon_name))
        if verbose:
            print 'command: %s' % command
        try:
            subprocess.check_output(command, shell=True).decode('utf-8')
        except Exception as e:
            raise e

    content = {'images': images, 'info': {'version': 1, 'author': 'xcode'}}
    json_content = json.dumps(content, indent=1)

    if verbose:
        print "image json content: %s" % json_content

    with open(os.path.join(app_icon_dist, 'Contents.json'), mode='w') as icon_content:
        icon_content.write(json_content)


def head_ico_make(source, resource, verbose):
    if verbose:
        print 'update head ico'
    head_ico_path = os.pardir.join(source, 'RubikU-Popular', 'RubikU-Popular', 'URMain', 'URHomePage', 'Resources',
                                   'URHomePageImages.xcassets', 'ur_home_title_icon.imageset')

    head_img = os.path.join(resource, '医院logo@3x.png')
    if os.path.exists(head_img):
        raise ValueError("医院logo图片没有上传")

    for f in os.listdir(head_ico_path):
        if f.endswith('.png'):
            os.remove(os.path.join(head_ico_path, f))

    for icon in ico_list:
        s = icon['size']
        multiple = icon['multiple']
        size = int(s * multiple)

        icon_name = HEAD_ICO % (size)

        command = 'convert -resize %sx%s  %s  %s' % (
            size, size, head_img, os.path.join(head_ico_path, icon_name))
        if verbose:
            print 'command: %s' % command
        try:
            subprocess.check_output(command, shell=True).decode('utf-8')
        except Exception as e:
            raise e