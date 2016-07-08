#!/bin/bash

# Author            : Derek Maier
# Date Created      : 14 May 2016
# Last Revision     : 14 May 2016
# Version           : 0.1

# Software Versions :
#     wpa_supplicant

# ====================
#   Description
# ====================
# use wpa_passphrase to initialize configuration file

dev="wlan0"
ifconfig $dev up
wpa_supplicant  -B  -i $dev -c /etc/wpa_supplicant.conf &
dhclient $dev &
