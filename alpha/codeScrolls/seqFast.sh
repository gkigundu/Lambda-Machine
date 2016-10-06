#!/bin/bash

index=0
while [ $index -lt 40 ] ; do
	echo "out_$index"
	index=$(($index+1))
	echo "err_$index" >&2
done
