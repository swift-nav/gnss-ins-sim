#!/bin/bash

CORES=`getconf _NPROCESSORS_ONLN`

if [ "$1" != "" ]; then

	i=0
	for res in $1/results*/;
	do
		i=$((i+1))
		b=$((i%CORES))

		python ./analyze_dr_trajectories.py --plotlim=2.0 --writecsv=$1.csv $res &
		sleep 1
		if [ $b -eq 0 ]
		then
			echo "Waiting for batch of ${CORES} jobs to complete..."
			wait
		fi
	done
	wait
	cp resultsviewer.html $1/resultsviewer.html

else
    echo "Usage:"
    echo "  ./parallelana <results-root-dir>"
fi

