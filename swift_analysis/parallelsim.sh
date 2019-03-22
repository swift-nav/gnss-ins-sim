#!/bin/bash -x

N=100
DUR=10
CORES=`getconf _NPROCESSORS_ONLN`

# This will be a little inefficient, but we will launch in batches 
# then wait for the entire batch to finish

EPOCH=`date +%s`
ROOTDIR=results-$EPOCH

mkdir -p $ROOTDIR

i=0
for TRAJ in 'CVSL'
do
	for ODOM in 'perfectwheelodom' 'none' # 'nhc'
	do
		for VIBRATION in 'smooth' # 'bumpy'
		do
			for IMU in 'bmi160' # 'had300' 'bmw_typ' 'bmw_max'  
			do
				for SPEED in 55 112
				do
					i=$((i+1))
					b=$((i%CORES))
					ipp=`printf "%05d" $i`
					OUTDIR="$ROOTDIR/results-${ipp}-${IMU}-${SPEED}-${VIBRATION}-${ODOM}-${TRAJ}"
					python ./generate_dr_trajectories.py --outdir=$OUTDIR --N=$N --dur=$DUR --speed=$SPEED --imu=$IMU --vibrations=$VIBRATION --dynamics=$ODOM --traj=$TRAJ >> $ROOTDIR/sim$ipp.log &
					echo $! >> $ROOTDIR/sim$ipp.pid
					sleep 1
					if [ $b -eq 0 ]
					then
						echo "Waiting for batch of ${CORES} jobs to complete..."
						wait
					fi
				done
			done
		done
	done
done
wait