import threading
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pygame  # Legg til denne importen

# Initialiser pygame mixer
pygame.mixer.init()

# Filnavn for input
input_file = "/Users/brageskikstadengeland/Desktop/Egenprog/Værdata_Kroksjøen/Parameter_output.txt"

def play_alert_sound():
    try:
        # Angi banen til lydfilen
        lydfil = 'Værdata_Kroksjøen/Old_ringing.mp3'  # Oppdater banen om nødvendig
        
        # Last inn lydfilen
        pygame.mixer.music.load(lydfil)
        
        # Spill av lydfilen
        pygame.mixer.music.play()
        
        # Vent til lydavspillingen er ferdig
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Vent litt for å unngå å fryse programmet
    except Exception as e:
        print(f"Kunne ikke spille av lyd: {e}")

def kite_mode(test_mode=False):
    from Værdata_plot import plot_live_data
    print("\nStarter kite-modus. Programmet vil varsle deg når vindhastigheten overstiger 5 m/s.")
    print("Programmet vil sjekke vindhastigheten og oppdatere grafen hvert minutt.")
    print("Meldinger om vindhastigheten skrives ut hvert 10. minutt.")
    print("Trykk Ctrl+C for å avslutte kite-modus.\n")
    
    siste_oppdatering = datetime.now() - timedelta(minutes=10)  # For å sikre at vi får en oppdatering med en gang
    
    try:
        while True:
            # Les siste vindhastighet fra filen
            with open(input_file, 'r') as file:
                lines = file.readlines()
                if len(lines) < 2:
                    print("Ingen data tilgjengelig ennå.")
                else:
                    last_line = lines[-1]
                    parts = last_line.strip().split('|')
                    if len(parts) == 5:
                        vind = float(parts[0].strip())
                        tidspunkt_str = parts[3].strip()
                        dato_str = parts[4].strip()
                        dato_tid = tidspunkt_str + " " + dato_str
                        tidspunkt = datetime.strptime(dato_tid, '%H:%M %d.%m.%Y')

                        nåværende_tid = datetime.now()
                        tid_siden_siste_oppdatering = (nåværende_tid - siste_oppdatering).total_seconds() / 60.0

                        # Sjekk om vindhastigheten overstiger 5 m/s
                        if test_mode or vind >= 5.0:
                            if test_mode:
                                print(f"[{tidspunkt.strftime('%d.%m.%Y %H:%M')}] Testmodus - spiller av lyd uavhengig av vindhastighet.")
                            else:
                                print(f"[{tidspunkt.strftime('%d.%m.%Y %H:%M')}] Vindhastighet er {vind} m/s - Det blåser nok til å kite!")
                            # Spill av en lyd
                            play_alert_sound()
                            # Oppdater siste oppdateringstid for å unngå dupliserte meldinger
                            siste_oppdatering = nåværende_tid
                        else:
                            # Kun skrive ut melding hvert 10. minutt
                            if tid_siden_siste_oppdatering >= 10:
                                print(f"[{tidspunkt.strftime('%d.%m.%Y %H:%M')}] Vindhastighet er {vind} m/s - Ikke nok vind.")
                                siste_oppdatering = nåværende_tid

                        # Oppdater grafen hvert minutt
                        print("Oppdaterer graf over de siste 2 timene...\n")
                        plot_live_data(smoothing_method='moving_average', hours_back=2, daytime_only=False, moving_average_window=6)
                    else:
                        print("Feil ved lesing av data.")

            # Vent i 1 minutt før neste sjekk
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nAvslutter kite-modus.")
        pygame.mixer.quit()  # Lukk pygame mixer
