from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
from datetime import datetime
from threading import Event

def fetch_and_write_data(output_file, stop_event):
    # Konfigurer Chrome for headless modus
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Kjør uten GUI
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    try:
        while not stop_event.is_set():
            # Initialiserer headless Chrome-driveren
            driver = webdriver.Chrome(options=chrome_options)

            # Åpner nettsiden
            driver.get("https://kroksjoen.kartkongen.com/")

            # Venter litt for å la siden laste ferdig
            time.sleep(5)

            # Henter innholdet av nettsiden
            content = driver.page_source

            # Lukker driveren
            driver.quit()

            # Parser HTML-innholdet med BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')

            # Hent verdier fra nettsiden
            vindhastighet = None
            vindretning = None
            tidspunkt = None
            temperatur = None

            # Finn teksten for vindhastighet
            tspan_elements = soup.find_all('tspan', {'class': 'highcharts-text-outline'})
            for element in tspan_elements:
                try:
                    if element.text.strip():
                        vindhastighet = float(element.text.strip())
                        break
                except ValueError:
                    print("Ugyldig vindhastighet, hopper over denne verdien.")
                    continue

            # Finn teksten for vindretning
            wind_direction = soup.find('div', {'id': 'windDirectionText'})
            if wind_direction:
                vindretning = wind_direction.text.strip()

            # Finn klokkeslettet for målingen
            time_element = soup.find('text', {'class': 'highcharts-axis-title'})
            if time_element:
                time_tspan = time_element.find('tspan')
                if time_tspan:
                    tidspunkt = time_tspan.text.strip()

            # Finn temperaturen
            temperature = soup.find('span', {'id': 'temperatureValue'})
            try:
                if temperature and temperature.text.strip():
                    temperatur = float(temperature.text.strip())
            except ValueError:
                print("Ugyldig temperatur, hopper over denne verdien.")
                temperatur = None

            # Hent gjeldende dato
            dato = datetime.now().strftime("%d.%m.%Y")  # Format: DD.MM.YYYY

            # Legg til output i filen hvis alle verdier er funnet og gyldige
            if vindhastighet is not None and vindretning and tidspunkt and temperatur is not None:
                with open(output_file, 'a') as file:
                    file.write(f"{vindhastighet} | {vindretning} | {temperatur} | {tidspunkt} | {dato}\n")
            else:
                print("Noen data mangler eller er ugyldige, ingenting blir skrevet til filen.")

            # Vent 60 sekunder eller til stop_event er satt
            stop_event.wait(60)

    except KeyboardInterrupt:
        print("Programmet for å hente og skrive data ble stoppet manuelt.")
    finally:
        print("Henting og skriving av data ferdig.")

      
        
        
import time
import os

def monitor_and_print_data(output_file):
    """
    Overvåker output_file for nye linjer og skriver dem ut til konsollen.
    Denne funksjonen vil kjøre til brukeren avbryter med Ctrl+C.
    """
    try:
        with open(output_file, 'r') as file:
            # Gå til slutten av filen for å begynne overvåkingen
            file.seek(0, os.SEEK_END)
            print(f"Overvåker filen: {output_file}")
            print("Trykk Ctrl+C for å stoppe overvåkingen og gå tilbake til hovedmenyen.\n")
            
            while True:
                line = file.readline()
                if not line:
                    # Ingen nye linjer, vent et øyeblikk før neste sjekk
                    time.sleep(1)
                    continue
                print(f"Data skrevet til fil: {line.strip()}")
    except FileNotFoundError:
        print(f"Filen {output_file} ble ikke funnet.")
    except KeyboardInterrupt:
        print("\nOvervåkingen ble stoppet av brukeren.")
    except Exception as e:
        print(f"En feil oppstod: {e}")
