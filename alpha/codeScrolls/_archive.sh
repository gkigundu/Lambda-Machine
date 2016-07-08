#!/bin/bash

# Author            : Derek Maier
# Date Created      : 22 June 2016
# Last Revision     : 22 June 2-16
# Version           : 0.1

# Software Versions :
#     find (GNU findutils) 4.4.2

# ====================
#   Description
# ====================
# Archives the content of the directory the script is placed in.
# This will move all files in to a folder in the same directory as the
# script called _Archive. It will tag each file with a timestamp based
# on epoch time.
# Note : The script will not delete files.

dir="$HOME/Downloads/"

dir=$(echo $dir | sed 's@/\+$@@g')
if [ ! -d "$dir/_Archive" ] ; then
	mkdir "$dir/_Archive"
fi
find ~/Downloads/* -maxdepth 0 |sed 's#.*/##' |grep -v "^_" | while read x; do
	echo mv "$dir/$x" "$dir/_Archive/$(date +%s)-$x"
	mv "$dir/$x" "$dir/_Archive/$(date +%s)-$x"
done
