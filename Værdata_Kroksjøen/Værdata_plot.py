import threading
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
import collections
from Vindretning_bilde import draw_wind_direction_arrow
from Værdata_analyse import fetch_and_write_data, monitor_and_print_data
from Smooth_curves import spline_interpolation, moving_average
from Kite_mode import kite_mode  # Importer fra common_functions.py

# Filnavn for input
input_file = "Værdata_Kroksjøen/Parameter_output.txt"

# Funksjon for å lese data fra filen
def read_and_plot_data(hours_back=None, daytime_only=False):
    tidspunkter = []
    vindhastighet = []
    temperatur = []
    vindretning = []

    # Les data fra filen
    with open(input_file, 'r') as file:
        lines = file.readlines()[1:]  # Hopper over header-linjen hvis det er en

        data_dict = collections.OrderedDict()
        for line in lines:
            parts = line.strip().split('|')
            if len(parts) == 5:
                try:
                    vind = float(parts[0].strip())
                except ValueError:
                    print(f"Ugyldig vindhastighet i linje: {line}")
                    continue
                retning = parts[1].strip()
                try:
                    temp = float(parts[2].strip())
                except ValueError:
                    print(f"Ugyldig temperatur i linje: {line}")
                    continue
                tidspunkt_str = parts[3].strip()
                dato_str = parts[4].strip()
                dato_tid = tidspunkt_str + " " + dato_str

                try:
                    tidspunkt = datetime.strptime(dato_tid, '%H:%M %d.%m.%Y')
                except ValueError as ve:
                    print(f"Feil ved parsing av dato og tid: {ve}")
                    print(f"Linja som forårsaket feil: {line}")
                    continue

                if tidspunkt not in data_dict:
                    data_dict[tidspunkt] = {
                        'vindhastighet': [vind],
                        'temperatur': [temp],
                        'vindretning': [retning]
                    }
                else:
                    data_dict[tidspunkt]['vindhastighet'].append(vind)
                    data_dict[tidspunkt]['temperatur'].append(temp)
                    data_dict[tidspunkt]['vindretning'].append(retning)

    if hours_back is not None:
        nå = datetime.now()
        tidsgrense = nå - timedelta(hours=hours_back)
    else:
        tidsgrense = None

    sorted_timestamps = sorted(data_dict.keys())
    for tidspunkt in sorted_timestamps:
        if tidsgrense is not None and tidspunkt < tidsgrense:
            continue

        if daytime_only:
            if not (8 <= tidspunkt.hour < 16):
                continue

        tidspunkter.append(tidspunkt)
        vindhastighet.append(np.mean(data_dict[tidspunkt]['vindhastighet']))
        temperatur.append(np.mean(data_dict[tidspunkt]['temperatur']))
        vindretning.append(data_dict[tidspunkt]['vindretning'][0])  # Juster etter behov

    # Sjekk for dupliserte tidsstempler
    if len(tidspunkter) != len(set(tidspunkter)):
        print("Advarsel: Det finnes dupliserte tidsstempler etter filtrering.")

    return tidspunkter, vindhastighet, temperatur, vindretning


# Funksjon for å plotte data live
def plot_live_data(smoothing_method='moving_average', hours_back=None, daytime_only=False, moving_average_window=20):
    tidspunkter, vindhastighet, temperatur, vindretning = read_and_plot_data(hours_back, daytime_only)

    if len(tidspunkter) == 0:
        print("Ingen data tilgjengelig for de valgte filtrene.")
        return

    # Sorter dataene
    tidspunkter, vindhastighet, temperatur, vindretning = zip(*sorted(zip(tidspunkter, vindhastighet, temperatur, vindretning)))

    # Konverter tidspunkter til numre for plotting (kun nødvendig for moving_average)
    tidsverdier = mdates.date2num(tidspunkter)

    # Anvende glatting
    if smoothing_method == 'spline':
        # Korrekt utpakking av spline_interpolation returnerte verdier
        tidspunkter_smooth, vindhastighet_smooth = spline_interpolation(tidspunkter, vindhastighet)
        tidspunkter_smooth, temperatur_smooth = spline_interpolation(tidspunkter, temperatur)
        vindretning_smooth = vindretning  # Spline glatter ikke vindretning
    elif smoothing_method == 'moving_average':
        vindhastighet_smooth = moving_average(vindhastighet, window_size=moving_average_window)
        temperatur_smooth = moving_average(temperatur, window_size=moving_average_window)
        vindretning_smooth = vindretning[len(vindretning) - len(vindhastighet_smooth):]
        tidspunkter_smooth = tidspunkter[len(tidspunkter) - len(vindhastighet_smooth):]
    else:
        vindhastighet_smooth = vindhastighet
        temperatur_smooth = temperatur
        vindretning_smooth = vindretning
        tidspunkter_smooth = tidspunkter

    # Konverter tidspunkter_smooth til numeriske verdier for vindretningspiler
    tidsverdier_smooth_num = mdates.date2num(tidspunkter_smooth)

    # Opprett figuren og aksene
    fig, ax1 = plt.subplots(figsize=(10, 6))  # Juster figurstørrelsen etter behov
    ax1.plot(tidspunkter_smooth, vindhastighet_smooth, 'r-', label='Vindhastighet (m/s)')
    ax1.set_xlabel('Tid')
    ax1.set_ylabel('Vindhastighet (m/s)', color='r')
    ax1.tick_params(axis='y', labelcolor='r')

    ax2 = ax1.twinx()
    ax2.plot(tidspunkter_smooth, temperatur_smooth, 'b-', label='Temperatur (°C)')
    ax2.set_ylabel('Temperatur (°C)', color='b')
    ax2.tick_params(axis='y', labelcolor='b')

    # Oppdater y-aksen
    ax1.relim()
    ax1.autoscale_view()
    ax2.relim()
    ax2.autoscale_view()

    # Beregn x-akse dataområde for å skalere pilene
    x_data_span = max(tidsverdier_smooth_num) - min(tidsverdier_smooth_num)
    desired_arrow_length_fraction = 0.02  # Ønsket pilens lengde som fraksjon av x_data_span
    arrow_length = desired_arrow_length_fraction * x_data_span  # Dynamisk lengde

    # Sett y_offset til å være litt over den øvre x-aksen i axes fraction
    y_offset = 0.98  # Justert for å unngå clipping

    # Tegn vindpilene kun ved x-ticks innenfor buffer
    arrow_annotations = []
    x_ticks_num = ax1.get_xticks()

    # Definer buffer for å unngå piler ved margene
    min_x = min(tidsverdier_smooth_num)
    max_x = max(tidsverdier_smooth_num)
    x_buffer = 0.02 * (max_x - min_x)  # 2% buffer

    for x_tick in x_ticks_num:
        if (x_tick < min_x + x_buffer) or (x_tick > max_x - x_buffer):
            continue  # Skip ticks nær plottemargene
        # Finn nærmeste tidspunkt i dataene til x_tick
        closest_idx = np.argmin(np.abs(tidsverdier_smooth_num - x_tick))
        if closest_idx < len(vindretning_smooth):
            direction = vindretning_smooth[closest_idx]
            annotation = draw_wind_direction_arrow(ax1, x_tick, direction, y_offset=y_offset, arrow_length=arrow_length)
            if annotation:
                arrow_annotations.append(annotation)

    # Formater x-aksen
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y %H:%M'))
    fig.autofmt_xdate()

    # Fjern tittelen hvis nødvendig
    # plt.title('Vindhastighet, temperatur og vindretning over tid')  # Kommentert ut

    # Legg til grid
    ax1.grid(True)

    # Juster x-aksen basert på dataene
    if tidspunkter_smooth:
        min_tidspunkt = min(tidspunkter_smooth)
        max_tidspunkt = max(tidspunkter_smooth)
        ax1.set_xlim([min_tidspunkt, max_tidspunkt])

    # Justere layout for å unngå klipping av pilene
    fig.subplots_adjust(top=0.90)  # Juster top margin etter behov, f.eks. 0.90 eller 0.95

    plt.show()

# Funksjon for å skrive data til konsoll
def print_data_to_console(output_file):
    """
    Leser data fra output_file og skriver dem ut til konsollen.
    """
    try:
        with open(output_file, 'r') as file:
            lines = file.readlines()
            # Sjekk om første linje er en header og hopp over den
            if lines and "Vindhastighet" in lines[0]:
                lines = lines[1:]
            if not lines:
                print("Ingen data tilgjengelig.")
                return
            for line in lines:
                print(f"Data skrevet til fil: {line.strip()}")
    except FileNotFoundError:
        print(f"Filen {output_file} ble ikke funnet.")
    except Exception as e:
        print(f"En feil oppstod: {e}")

# Hovedprogrammet
if __name__ == "__main__":
    # Start tråden for å hente og skrive data til fil
    stop_event = threading.Event()
    fetch_thread = threading.Thread(target=fetch_and_write_data, args=(input_file, stop_event))
    fetch_thread.start()

    continue_program = True

    while continue_program:
        print("\nVelg en modus:")
        print("1: Plot graf")
        print("2: Data fra siste N timer")
        print("3: Kun dagtidsdata (kl. 08:00 til 16:00)")
        print("4: Kite-modus (varsle ved vind over 5 m/s)")
        print("5: Skriv data til konsoll")  # Nytt valg
        print("6: Avslutt programmet")  # Oppdatert
        mode_input = input("Skriv inn tallet for ønsket modus: ").strip()


        # Bruker match-case for å håndtere valg (Python 3.10+)
        match mode_input:
            case '1':
                # Brukeren ønsker å plotte grafen
                # Spør om plottemetode
                print("\nVelg plottemetode:")
                print("1: Spline glatting")
                print("2: Moving Average glatting")
                print("3: Ingen glatting (default er Moving Average hvis ingen valg tas)")
                smoothing_choice = input("Skriv inn tallet for ønsket plottemetode: ").strip()

                match smoothing_choice:
                    case '1':
                        smoothing_method = 'spline'
                    case '2':
                        smoothing_method = 'moving_average'
                    case '3':
                        smoothing_method = 'none'
                    case _:
                        print("Ugyldig valg. Bruker 'moving_average' som standard.")
                        smoothing_method = 'moving_average'

                # Ingen filtrering
                hours_back = None
                daytime_only = False

                # Start plotting med valgt glattingmetode uten filtrering
                plot_live_data(smoothing_method=smoothing_method, hours_back=hours_back, daytime_only=daytime_only)

            case '2':
                # Modus for å vise data fra siste N timer
                while True:
                    try:
                        hours_back = int(input("Hvor mange timer tilbake vil du se data fra? Skriv et heltall: "))
                        break
                    except ValueError:
                        print("Ugyldig input. Vennligst skriv et heltall.")

                # Bruk 'moving_average' som standard plottemetode
                smoothing_method = 'moving_average'
                daytime_only = False

                # Plot data med filtrering på antall timer
                plot_live_data(smoothing_method=smoothing_method, hours_back=hours_back, daytime_only=daytime_only)

            case '3':
                # Modus for å vise kun dagtidsdata
                daytime_only = True
                hours_back = None
                # Bruk 'moving_average' som standard plottemetode
                smoothing_method = 'moving_average'

                # Plot data med dagtidsfiltrering
                plot_live_data(smoothing_method='none', hours_back=hours_back, daytime_only=daytime_only)

            case '4':
                # Kite-modus
                test_input = input("Vil du kjøre kite-modus i testmodus? (ja/nei): ").strip().lower()
                test_mode = test_input == 'ja'
                kite_mode(test_mode=test_mode)

            case '5':
                # Ny modus: Skriv data til konsoll
                print("\nSkriver data til konsoll...")
                monitor_and_print_data(input_file)

            case '6':
                print("Avslutter programmet...")
                continue_program = False
                stop_event.set()
                break

            case _:
                print("Ugyldig valg. Vennligst velg et tall mellom 1 og 6.")

    # Vent på at datainnsamlingstråden skal avslutte
    fetch_thread.join()
    print("Programmet er avsluttet.")
