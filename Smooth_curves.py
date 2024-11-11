import numpy as np
from scipy.interpolate import make_interp_spline
import matplotlib.dates as mdates

def moving_average(data, window_size):
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')



# Smooth_curves.py
import numpy as np
from scipy.interpolate import make_interp_spline
import matplotlib.dates as mdates
from datetime import datetime

def moving_average(data, window_size):
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

def spline_interpolation(x, y, num_points=400):
    # Sjekk at x er en liste av datetime-objekter
    if not all(isinstance(dt, datetime) for dt in x):
        raise TypeError("Alle elementer i x må være datetime-objekter.")

    # Fjern tzinfo for naive datetime-objekter
    x_naive = [dt.replace(tzinfo=None) if dt.tzinfo else dt for dt in x]

    # Konverter datetime til numerisk format
    x_num = mdates.date2num(x_naive)

    # Sørg for at dataene er sortert etter tid
    sorted_indices = np.argsort(x_num)
    x_num_sorted = x_num[sorted_indices]
    y_sorted = np.array(y)[sorted_indices]

    # Fjern duplikater ved å beholde første forekomst
    unique_x, unique_indices = np.unique(x_num_sorted, return_index=True)
    unique_y = y_sorted[unique_indices]

    # Debugging: Sjekk at unique_x er numerisk
    #print(f"unique_x type: {unique_x.dtype}, unique_x sample: {unique_x[:5]}")
    #print(f"unique_y type: {unique_y.dtype}, unique_y sample: {unique_y[:5]}")

    if len(unique_x) < 4:
        raise ValueError("For få unike punkter for spline interpolasjon. Minst 4 unike punkter kreves.")

    # Opprett spline-funksjonen
    spline = make_interp_spline(unique_x, unique_y, k=3)

    # Opprett en finere x-akse
    x_fine = np.linspace(unique_x.min(), unique_x.max(), num_points)
    y_smooth = spline(x_fine)

    # Konverter x_fine tilbake til datetime-objekter
    x_smooth = mdates.num2date(x_fine)
    x_smooth = [dt.replace(tzinfo=None) if dt.tzinfo else dt for dt in x_smooth]

    return x_smooth, y_smooth
