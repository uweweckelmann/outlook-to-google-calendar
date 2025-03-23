import requests
from datetime import datetime, timedelta
import pytz

# URL des Outlook-Kalenders
OUTLOOK_ICS_URL = 'https://outlook.office365.com/owa/calendar/1f33ba88713f4be89407aa4efcafbbc0@svwestfalen.de/4d297caa680842f495fe97af6ea95ede15552394813414379089/S-1-8-939608001-31717856-4038653985-2387835883/reachcalendar.ics'

# Zeitzone definieren
BERLIN_TZ = pytz.timezone('Europe/Berlin')

def convert_utc_to_berlin(dt_str):
    """Konvertiert UTC-Zeitstring nach Europe/Berlin-Zeitstring."""
    utc_dt = datetime.strptime(dt_str, '%Y%m%dT%H%M%SZ')
    utc_dt = utc_dt.replace(tzinfo=pytz.utc)
    berlin_dt = utc_dt.astimezone(BERLIN_TZ)
    return berlin_dt.strftime('%Y%m%dT%H%M%S')

def main():
    # ICS-Datei herunterladen
    response = requests.get(OUTLOOK_ICS_URL)
    ics_content = response.text

    # Zeilenweise bearbeiten
    new_lines = []
    for line in ics_content.splitlines():
        if line.startswith('DTSTART:') or line.startswith('DTEND:'):
            dt_str = line.split(':')[1]
            if dt_str.endswith('Z'):
                dt_str = dt_str[:-1]  # 'Z' entfernen
                berlin_time = convert_utc_to_berlin(dt_str)
                new_line = f"{line.split(':')[0]};TZID=Europe/Berlin:{berlin_time}"
                new_lines.append(new_line)
                continue
        new_lines.append(line)

    # Neue ICS-Datei erstellen
    new_ics_content = '\n'.join(new_lines)
    with open('reachcalendar_converted.ics', 'w') as f:
        f.write(new_ics_content)

if __name__ == '__main__':
    main()
