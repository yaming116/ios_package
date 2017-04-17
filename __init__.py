#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import os
import subprocess
import io
import time
from mod_pbxproj import XcodeProject

# name = None
# source = os.path.abspath('.')
#
# if not name:
#     name = os.path.basename(source)
# xcworkspace = os.path.join(source, name, '%s.xcworkspace' % name)
# command = 'xcodebuild archive -workspace %s -scheme  %s -configuration Release ' \
#           '-derivedDataPath ./build -archivePat h  ./build/Products/test.xcarchive | xcpretty' % (xcworkspace, name)
# print command
# subprocess.check_call(command, shell=True)

path = '/Volumes/BAK/project/OnlineBuildServer/platform_config/platform/rubiku/ios/resource_dir/rubikuceshi/URPConfigFiles/Certificates/RubicX.mobileprovision'
print subprocess.check_call('/usr/libexec/PlistBuddy -c "Print Entitlements:aps-environment" /dev/stdin <<< $(/usr/bin/security cms -D -i %s' % path, shell=True)
