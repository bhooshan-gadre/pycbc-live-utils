#!/usr/bin/env python

import os
import sys
import glob
import time
import numpy as np
import datetime as dt
import matplotlib
matplotlib.use('agg')
import pylab as pl
import matplotlib.dates as md
from pylab import rcParams


rcParams['figure.figsize'] = 13, 6
rcParams['font.size'] = 12

log_wildcard = sys.argv[1]

today = time.strftime('%Y-%m-%d')

data = []

for input_file in glob.glob(log_wildcard): 
    #It will  not iterate over all the wildecarded files, unless the file string is command line passed within ''
    for line in file(input_file, 'r'):
        if 'node742' not in line or 'duty' not in line:
            continue

        fields = line.split()
        if fields[0] < today:
            continue

        timestamp = '{} {}'.format(fields[0], fields[1].split(',')[0])    ## timestamp -- Date and Time

        duty = float(fields[9].replace(',', ''))
        lag = float(fields[11])
        ndet = int(fields[13])
        
        data.append([timestamp, duty, lag, ndet])      ## Array for plotting

if not data:
    exit()

data = sorted(data) ##sorting time-stamp wise

lags = np.array([lag for _, _, lag, _ in data])
ndets = np.array([ndet for _, _, _, ndet in data])

lags_median_average = np.median( lags )

tstamp = np.array([ timestamp for timestamp, _, _, _ in data ])

day_time_array = np.array([  dt.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S') for date_time_str in tstamp ])
daysarray = np.array([ i.date() for i in day_time_array ])
datetime_to_float = np.array( [ int( d.strftime("%s")  )  for d in day_time_array] )

no_days = max( daysarray ) - min(daysarray)

date_list = [ min(daysarray) + dt.timedelta(days=x) for x in range(0, no_days.days + 2 )]
datetime_list_for_ticks = [  dt.datetime.combine( i, dt.time(00) ) for i in date_list ]

color = ['red', 'orange','blue', 'green']


index_list = np.arange(0, len(day_time_array))

for i in range(0, len(datetime_list_for_ticks)-1):
    index_list_datewise  = np.argwhere( ( day_time_array>=datetime_list_for_ticks[i])& 
                                        ( day_time_array<=datetime_list_for_ticks[i+1])).flatten()

    #print index_list_datewise
    
    ##print datetime_list_for_ticks[i]

    datetime_array_daywise = day_time_array[index_list_datewise]
    lags_daywise = lags[index_list_datewise]
    ndets_daywise = ndets[index_list_datewise]

    fig, ax = pl.subplots(2,1, sharex=True)
    
    ax[0].plot( datetime_array_daywise, lags_daywise, zorder=1, 
            lw= .5, color='#808080' )

    for ndet in np.unique(ndets):
        l = lags_daywise[ ndets_daywise  == ndet]
        color_array = np.where( ndets_daywise == ndet )[0] 
        day_time_array_det = datetime_array_daywise[ ndets_daywise  == ndet]
        ax[0].scatter(day_time_array_det, l, label='{} live detector(s)'.format(ndet),
                      marker='.', s=3, color=color[ndet], zorder=2)

    xfmt = md.DateFormatter('%Y-%m-%d\n%H:%M:%S PST')
    ax[0].xaxis.set_major_formatter(xfmt)
    ax[0].tick_params(axis='x')

    title = date_list[i].isoformat()
    ax[0].set_xlim( datetime_array_daywise[0], datetime_list_for_ticks[i+1])
    ax[0].set_ylim(1, 400)
    ax[0].set_yscale('log')
    ax[0].grid(True)
    ax[0].set_ylabel('PyCBC Live triggers-to-disk lag [s]')
    lgnd = ax[0].legend(ncol=2, loc='best')
    ax[0].set_title(title)

    ax[1].plot( datetime_array_daywise, ndets_daywise )
    xfmt = md.DateFormatter('%Y-%m-%d\n%H:%M:%S PST')
    ax[1].xaxis.set_major_formatter(xfmt)
    ax[1].tick_params( axis='x')
    ax[1].set_yticks( [0,1,2,3])
    ax[1].set_ylabel( "Live detectors' number")
    ax[1].grid(True)

    pl.tight_layout()

    out_base = os.path.join(sys.argv[2], date_list[i].strftime('%Y/%m/%d'))
    if not os.path.exists(out_base):
        os.makedirs(out_base)
    out_file_name = '{}_lag_over_time.png'.format(date_list[i])
    out_path = os.path.join(out_base, out_file_name)
    fig.savefig(out_path)
