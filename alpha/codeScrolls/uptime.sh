#!/bin/bash

index=0
while [ $index -lt 40 ] ; do
	uptime | tr '\n' '|'
        index=$(($index+1))
	sleep 1
done
