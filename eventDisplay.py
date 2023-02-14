import numpy as np

import matplotlib.pyplot as plt

import h5py

detector_bounds = [[-150, 150], [-150, 150], [0, 300]] # mm (x, y, z)

v_drift = 1.6 # mm/us (very rough estimate)
clock_interval = 0.1 # us/tick -- 10 MHz clock rate
drift_distance = detector_bounds[2][1] - detector_bounds[2][0] 

drift_window = drift_distance/(v_drift*clock_interval) # maximum drift time

drift_direction = 1 # +/- 1 depending on the direction of the drift in z

f = h5py.File('selftrigger_2022_08_05_05_06_01_PDT_evd.h5')

eventData = f['charge']['events']['data']

hitData = f['charge']['hits']['data']

# this is a list of pairs of ints
# the first is an event ID, the second is a hit ID
eventHitRefs = f['charge']['events']['ref']['charge']['hits']['ref']  

def drift_distance(dt):
    """
    Estimate the z-position of a drifting electron
    """
    return detector_bounds[2][0] + drift_direction*dt*clock_interval*v_drift

def draw_hits_in_event_window_by_timestamp(event):
    """
    Given a t0, plot all hits that would be within a 
    drift window within the detector timeline
    """
    t0 = event['ts_start']
    tf = event['ts_end']
    
    eventMask = ( t0 <= hitData['ts']) & (hitData['ts'] < tf ) 

    eventHits = hitData[eventMask]

    px = eventHits['px']
    py = eventHits['py']
    ts = eventHits['ts']

    z = drift_distance(ts - t0)

    q = eventHits['q']

    fig = plt.figure()
    ax = fig.add_subplot(111, projection = '3d')

    points = ax.scatter(px, py, z,
                        c = q)

    cb = fig.colorbar(points)
    cb.set_label(r'Charge')
    
    return ax

def draw_hits_in_event_window_by_reference(event):
    """
    This is another way of associating hits and events
    you can use the 'ref' table to make a mask instead of t0
    """
    eventID = event['id']

    t0 = event['ts_start']

    eventMask = eventHitRefs[:,0] == eventID

    eventHits = hitData[eventMask]

    px = eventHits['px']
    py = eventHits['py']
    ts = eventHits['ts']

    z = drift_distance(ts - t0)

    q = eventHits['q']

    fig = plt.figure()
    ax = fig.add_subplot(111, projection = '3d')

    ax.scatter(px, py, z,
               c = q)

    return ax

def draw_boundaries(ax):
    """
    Draw the detector boundaries as a wireframe
    not needed, but pretty
    """
    boundKwargs = {'color': 'black',
                   'ls': '--'}
    
    ax.plot([detector_bounds[0][0], detector_bounds[0][1]],
            [detector_bounds[1][0], detector_bounds[1][0]],
            [detector_bounds[2][0], detector_bounds[2][0]],
            **boundKwargs)
    ax.plot([detector_bounds[0][0], detector_bounds[0][1]],
            [detector_bounds[1][1], detector_bounds[1][1]],
            [detector_bounds[2][0], detector_bounds[2][0]],
            **boundKwargs)
    ax.plot([detector_bounds[0][0], detector_bounds[0][1]],
            [detector_bounds[1][0], detector_bounds[1][0]],
            [detector_bounds[2][1], detector_bounds[2][1]],
            **boundKwargs)
    ax.plot([detector_bounds[0][0], detector_bounds[0][1]],
            [detector_bounds[1][1], detector_bounds[1][1]],
            [detector_bounds[2][1], detector_bounds[2][1]],
            **boundKwargs)

    ax.plot([detector_bounds[0][0], detector_bounds[0][0]],
            [detector_bounds[1][0], detector_bounds[1][1]],
            [detector_bounds[2][0], detector_bounds[2][0]],
            **boundKwargs)
    ax.plot([detector_bounds[0][1], detector_bounds[0][1]],
            [detector_bounds[1][0], detector_bounds[1][1]],
            [detector_bounds[2][0], detector_bounds[2][0]],
            **boundKwargs)
    ax.plot([detector_bounds[0][0], detector_bounds[0][0]],
            [detector_bounds[1][0], detector_bounds[1][1]],
            [detector_bounds[2][1], detector_bounds[2][1]],
            **boundKwargs)
    ax.plot([detector_bounds[0][1], detector_bounds[0][1]],
            [detector_bounds[1][0], detector_bounds[1][1]],
            [detector_bounds[2][1], detector_bounds[2][1]],
            **boundKwargs)

    ax.plot([detector_bounds[0][0], detector_bounds[0][0]],
            [detector_bounds[1][0], detector_bounds[1][0]],
            [detector_bounds[2][0], detector_bounds[2][1]],
            **boundKwargs)
    ax.plot([detector_bounds[0][0], detector_bounds[0][0]],
            [detector_bounds[1][1], detector_bounds[1][1]],
            [detector_bounds[2][0], detector_bounds[2][1]],
            **boundKwargs)
    ax.plot([detector_bounds[0][1], detector_bounds[0][1]],
            [detector_bounds[1][0], detector_bounds[1][0]],
            [detector_bounds[2][0], detector_bounds[2][1]],
            **boundKwargs)
    ax.plot([detector_bounds[0][1], detector_bounds[0][1]],
            [detector_bounds[1][1], detector_bounds[1][1]],
            [detector_bounds[2][0], detector_bounds[2][1]],
            **boundKwargs)

    return ax

def draw_labels(ax):
    ax.set_xlabel(r'x [mm]')
    ax.set_ylabel(r'y [mm]')
    ax.set_zlabel(r'z (drift) [mm]')

    plt.tight_layout()

for event in eventData:
    ax = draw_hits_in_event_window_by_timestamp(event)
    # ax = draw_hits_in_event_window_by_reference(event)
    draw_boundaries(ax)
    draw_labels(ax)

    plt.show()
