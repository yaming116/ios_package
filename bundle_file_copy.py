#!/usr/bin/env python
# _*_ coding: utf-8 _*_

'copy bundle file'

import os.path as path
import shutil

image_list = ['ur_logo_icon.png',
              'ur_cyclepic_default.png',
              'urp_firstpage_slide1.png',
              'urp_firstpage_slide2.png',
              'urp_firstpage_slide3.png']


def check(image_resource, verbose):
    if verbose:
        print 'start check bundle image file'

    for image in image_list:
        p = path.join(image_resource, image)
        if not (path.exists(p)):
            raise ValueError('image not exist: %s' % p)


def copy(image_resource, app_image_folder_dist, verbose):
    if verbose:
        print 'start bundle image copy'
    for image in image_list:
        p = path.join(image_resource, image)
        shutil.copy(p, app_image_folder_dist)