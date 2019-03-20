#!/bin/bash -x

N=100
DUR=10

for ODOM in 0.0 0.001
do
	for VIBRATION in 'none' 'smooth-road'
	do
		for IMU in 'bmi160' 'bmw'
		do
			for SPEED in 12 33 55 112
			do
				OUTDIR="results-${IMU}-${SPEED}-${VIBRATION}"
				time python ./generate_dr_trajectories.py --outdir=$OUTDIR --N=$N --dur=$DUR --speed=$SPEED --imu=$IMU --vibrations=$VIBRATION --odom-sigma=$ODOM
			done
		done
	done
done