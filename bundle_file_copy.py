#!/usr/bin/env python
# _*_ coding: utf-8 _*_

'copy bundle file'

import os.path as path
import shutil

image_list = ['ur_logo_icon.png']


def check(bundle_json, image_resource, verbose):
    if verbose:
        print 'start check bundle image file'
    if not bundle_json:
        bundle_json = image_list
    for image in bundle_json:
        p = path.join(image_resource, image)
        if not (path.exists(p)):
            raise ValueError('image not exist: %s' % p)


def copy(bundle_json, image_resource, app_image_folder_dist, verbose):
    if verbose:
        print 'start bundle image copy'

    if not bundle_json:
        bundle_json = image_list
    for image in bundle_json:
        p = path.join(image_resource, image)
        shutil.copy(p, app_image_folder_dist)