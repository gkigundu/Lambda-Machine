#!/bin/bash

# Author            : Derek Maier
# Date Created      : 19 June 2016
# Last Revision     : 24 June 2016
# Version           : 0.1

# Software Versions :
#     cgpt      // can be found in this repository @ XDerekMaierX/BashTools/cgpt-armv7l/cgpt
#     mkfs.ext4

# ====================
#   Description
# ====================
# Creates a bootable device for a Google Chromebook armv7l based on Arch Linux
# Tested on chromebook C100PA
# These instructions were derived from https://archlinuxarm.org/platforms/armv7/rockchip/asus-chromebook-flip-c100p
# This bootable disk will probably boot on other arm7l architectures like Raspberry Pi.
# Once booted into Arch Linux use the following to activate wifi : wifi-menu
# Default Info:
#     User: root
#     Pass: root
# If you would like to replace your primary ChromeOS with Arch Linux you can do the following:
#     Create this boot disk onto external media i.e. USB
#     Boot into USB
#     Delete ChromeOS (may require the removal of a readonly screw)
#     execute this script again using the primary HDD/SSD
# Note: Running from USB is much slower then using HDD/SSD

dev="/dev/mmcblk1"
devP1=$(echo $dev)p1
devP2=$(echo $dev)p2

# check dependencies
function checkRequirements {
  declare -a RequiredProgs
  for c in $@; do
        hash $c 2>/dev/null || { RequiredProgs+=($c) ; }
  done
  if [ ${#RequiredProgs[@]} -gt 0 ] ; then
    echo >&2 "<ERROR> This program depends on the executables: [${RequiredProgs[*]}].  Aborting."
    exit 1
  fi
}
checkRequirements blockdev mkfs.ext4 wget umount tar dd sync chmod

if [ "$EUID" -ne 0 ]
  then echo "<ERROR> Please run as root"
  exit
fi

umount $dev*
echo -e "g\nw" | fdisk $dev
if [ ! -f cgpt ]; then
	wget https://github.com/XDerekMaierX/BashTools/raw/master/cgpt-armv7l/cgpt
fi
chmod +x cgpt

./cgpt create $dev
./cgpt add -i 1 -t kernel -b 8192 -s 32768 -l Kernel -S 1 -T 5 -P 10 $dev
offset=$(./cgpt show $dev | grep "Sec GPT table" | awk '{print $1}')
./cgpt add -i 2 -t data -b 40960 -s $(( $offset - 40960 )) -l Root $dev
sudo blockdev --rereadpt $dev
mkfs.ext4 $devP2

cd /tmp
if [ ! -f /tmp/ArchLinuxARM-veyron-latest.tar.gz ]; then
	wget http://os.archlinuxarm.org/os/ArchLinuxARM-veyron-latest.tar.gz
fi
mkdir root
mount $devP2 root
tar -xf ArchLinuxARM-veyron-latest.tar.gz -C root
dd if=root/boot/vmlinux.kpart of=$devP1
umount root
sync
