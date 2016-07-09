#!/bin/bash

# Author            : Derek Maier
# Date Created      : 1 April 2016
# Last Revision     : 1 April 2016
# Version           : 0.1

# Software Versions :
#     opam
#     google-drive-ocamlfuse
#     fuse

# ====================
#   Description
# ====================

sudo apt-get install opam m4 libcurl4-gnutls-dev libfuse-dev libsqlite3-dev zlib1g-dev libncurses5-dev
opam init
opam update
opam install google-drive-ocamlfuse
alias gdrive='~/.opam/system/bin/google-drive-ocamlfuse'
echo "alias gdrive='~/.opam/system/bin/google-drive-ocamlfuse'" >> ~/.bashrc

# run 'gdrive' to initiate sign in. This requires a display. Use VPN for headless mode.
