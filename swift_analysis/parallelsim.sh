#!/bin/bash -x

N=500
DUR=10

for ODOM in 'none' 'perfect'
do
	for VIBRATION in 'none' 'smooth'
	do
		for IMU in 'bmi160' 'bmw'
		do
			for SPEED in 12 33 55 112
			do
				OUTDIR="results-${IMU}-${SPEED}-${VIBRATION}-${ODOM}"
				sleep 2
				time python ./generate_dr_trajectories.py --outdir=$OUTDIR --N=$N --dur=$DUR --speed=$SPEED --imu=$IMU --vibrations=$VIBRATION --odometry=$ODOM &
			done
		done
	done
done