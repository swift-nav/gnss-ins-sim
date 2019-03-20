#!/bin/bash -x

for res in results*/;
do
	python ./analyze_dr_trajectories.py $res
done