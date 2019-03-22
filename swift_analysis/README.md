# Swift Dead Reckoning Simulation

## Usage

- Step 1: Run many simulations across a specified trajectory.
- Step 2: Analyze noise across results

Run with no wheel odometry, with road vibrations:
```bash
python ./generate_dr_trajectories.py --outdir=./results --N=100 --dur=10 --speed=55 --imu=bmi160 --vibrations=smooth
```

Run with wheel odometry, with road vibrations:
```bash
python ./generate_dr_trajectories.py --outdir=./results --N=100 --dur=10 --speed=55 --imu=bmi160 --vibrations=smooth --odometry=perfect
```

Analyze resulting trajectories:

```bash
python ./analyze_dr_trajectories.py ./results
```

## Running many simulations

```bash
./parallelsim.sh
```

Edit the file for different options



