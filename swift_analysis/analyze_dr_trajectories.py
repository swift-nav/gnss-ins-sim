# Copyright (C) 2018 Swift Navigation Inc.
# Contact: <dev@swiftnav.com>
#
# This source is subject to the license found in the file 'LICENSE' which must
# be be distributed together with this source. All other rights reserved.
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND,
# EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.

import sys
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os.path
import os
import sys
import argparse

import generate_dr_trajectories


def analyze(resultsdir, writecsv=None, plotlim=0.0):
    resultsdir = os.path.abspath(resultsdir)
    resultsname = os.path.split(resultsdir)[-1]

    # I don't know how to use dataframes so I do this the stupid way.
    COL_TIME = 'time (sec)'
    COL_DUT_LAT = 'pos_lat (deg)'
    COL_DUT_LON = 'pos_lon (deg)'
    COL_DUT_ALT = 'pos_alt (m)'
    COL_REF_LAT = 'ref_pos_lat (deg)'
    COL_REF_LON = 'ref_pos_lon (deg)'
    COL_REF_ALT = 'ref_pos_alt (m)'
    # Earth radius at 32deg Lat.
    EARTHRAD = 6372168.
    D2R = np.pi / 180.

    times = []
    hori_errors = []
    vert_errors = []
    atrack_errors = []
    ctrack_errors = []
    hori_errors_end = []
    hori_errors_at = {}
    for f in glob.glob("{}/dr_*.csv".format(resultsdir)):
        df = pd.read_csv(f) 
        t = df[COL_TIME].values    
        dut_lat = df[COL_DUT_LAT].values
        dut_lon = df[COL_DUT_LON].values
        dut_alt = df[COL_DUT_ALT].values
        ref_lat = df[COL_REF_LAT].values
        ref_lon = df[COL_REF_LON].values
        ref_alt = df[COL_REF_ALT].values

        times.append(t)
        dut_y = EARTHRAD * D2R * dut_lat 
        dut_x = EARTHRAD * D2R * dut_lon * np.cos(D2R * 32.)
        ref_y = EARTHRAD * D2R * ref_lat
        ref_x = EARTHRAD * D2R * ref_lon * np.cos(D2R * 32.)
        vert_errors.append(np.abs(ref_alt - dut_alt))
        hori = np.linalg.norm([ref_x - dut_x, ref_y - dut_y], axis=0)

        ## find index of time
        interval = range(1,int(np.floor(t[-1]))+1)
        interval.append(t[-1]) 
        for ti in interval:
            if ti not in hori_errors_at:
                hori_errors_at[ti] = []
            hori_errors_at[ti].append(hori[np.argmax(t>=ti)])

        hori_errors.append(hori)
        atrack_errors.append((ref_y - dut_y)[-1])
        ctrack_errors.append((ref_x - dut_x)[-1])



    fig = plt.figure(figsize=(12,6))
    plt.subplot(221)
    plt.scatter(np.ravel(times)[::1], np.ravel(hori_errors)[::1], color=(0., 0., 1., 0.05), marker='x', s=1)
    plt.title("Horizontal Error Magnitude")
    plt.xlabel("t (s)")
    plt.ylabel("error (m)")
    if plotlim > 0.0:
        plt.ylim(0, plotlim)
    plt.subplot(223)
    plt.scatter(np.ravel(times)[::10], np.ravel(vert_errors)[::10], color=(0., 0., 1., 0.05), marker='x', s=1)
    plt.title("Vertical Error Magnitude")
    plt.xlabel("t (s)")
    plt.ylabel("error (m)")
    if plotlim > 0.0:
        plt.ylim(0, plotlim)
    plt.subplot(122)
    plt.scatter(np.ravel(ctrack_errors), np.ravel(atrack_errors), color=(0., 0., 1., 0.7), marker='o', s=6)
    plt.title("Error Scatter")
    plt.xlabel("Horizontal Cross-Track Error (m)")
    plt.ylabel("Horizontal Along-Track Error (m)")
    plt.gca().set_aspect('equal', 'datalim')
    ulim = np.max([np.max(np.abs(ctrack_errors)), np.max(np.abs(atrack_errors))])*1.2
    if plotlim > 0.0:
        ulim = plotlim
    plt.xlim(-ulim, ulim)
    plt.ylim(-ulim, ulim)
    fig.savefig(resultsdir.rstrip("/") + "-analytics.png")

    hori_errors_stats_at = {}
    for ti in hori_errors_at.keys():
        hori_errors_at[ti] = np.sort(hori_errors_at[ti])
        hori_errors_at_ti = hori_errors_at[ti]

        ind50 = int(np.floor(0.50*len(hori_errors_at_ti)))
        ind955 = int(np.floor(0.955*len(hori_errors_at_ti)))
        ind997 = int(np.floor(0.997*len(hori_errors_at_ti)))

        hori_errors_stats_at[ti] = {
            'mean': np.mean(hori_errors_at_ti),
            '50'  : hori_errors_at_ti[ind50],
            '95.5': hori_errors_at_ti[ind955],
            '99.7': hori_errors_at_ti[ind997]    
        }


    resultsparams = resultsname.split("-")
    if writecsv is not None and len(resultsparams) >= 6:
        # This came from parallel sims, so we dump results into CSV file
        STATSFILE = writecsv
        write_header = False
        if not os.path.isfile(STATSFILE):
            write_header = True

        ipp   = resultsparams[1]
        imu   = resultsparams[2]
        speed = resultsparams[3]
        vibe  = resultsparams[4]
        odom  = resultsparams[5]
        traj  = resultsparams[6]

        with open(STATSFILE, 'a+') as f:
            if write_header:
                leader = "IMU,Trajectory,Speed(mph),Vibration,Dynamic Model,"
                errors = ""
                for stat in sorted(hori_errors_stats_at[hori_errors_stats_at.keys()[0]].keys()):
                    for ti in hori_errors_stats_at.keys():
                        errors += "%s @ %ds," % (stat, np.round(ti))
                f.write("%s%s\n" % (leader, errors))

            f.write("%s,%s,%s,%s,%s," % (
                imu,
                traj,
                speed,
                vibe,
                odom))
            for stat in sorted(hori_errors_stats_at[hori_errors_stats_at.keys()[0]].keys()):
                for ti in hori_errors_stats_at.keys():
                    f.write("%f," % hori_errors_stats_at[ti][stat])
            f.write("\n")


        plt.show(block=False)
        print "Processed", ipp
    else:
        for ti in hori_errors_stats_at.keys():
            sys.stdout.write(str(ti))
            sys.stdout.write(",")
        sys.stdout.write("\n") 
        for stat in hori_errors_stats_at[hori_errors_stats_at.keys()[0]].keys():
            sys.stdout.write(stat)
            sys.stdout.write(",")
            for ti in hori_errors_stats_at.keys():
                sys.stdout.write(str(hori_errors_stats_at[ti][stat]))
                sys.stdout.write(",")
            sys.stdout.write("\n")
            sys.stdout.flush()

        plt.show()

if __name__ == "__main__":
    # Collect arguments.
    parser = argparse.ArgumentParser(description='Analyze DR trajectories.')
    parser.add_argument('--writecsv', type=str, required=False,
                        help='Write results to provided CSV file')
    parser.add_argument('--plotlim', type=float, default=0.,
                        help='IMU sample rate.')
    parser.add_argument('resultsdir', type=str,
                        help='The results directory to analyze')

    args = parser.parse_args()
    analyze(args.resultsdir, 
        writecsv=args.writecsv, 
        plotlim=args.plotlim)





