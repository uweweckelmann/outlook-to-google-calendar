import requests
import re
from datetime import datetime
import pytz

# ICS-Quelle
URL = 'https://outlook.office365.com/owa/calendar/1f33ba88713f4be89407aa4efcafbbc0@svwestfalen.de/4d297caa680842f495fe97af6ea95ede15552394813414379089/S-1-8-939608001-31717856-4038653985-2387835883/reachcalendar.ics'

# Berlin-Zeitzone
BERLIN_TZ = pytz.timezone("Europe/Berlin")

# ICS-Datei herunterladen
response = requests.get(URL)
ics = response.text

# VTIMEZONE-Block vollständig entfernen
ics = re.sub(r"BEGIN:VTIMEZONE.*?END:VTIMEZONE\r?\n", "", ics, flags=re.DOTALL)

# Microsoft-TZIDs ersetzen
ics = ics.replace("TZID=W. Europe Standard Time", "TZID=Europe/Berlin")
ics = ics.replace("TZID:W. Europe Standard Time", "TZID=Europe/Berlin")
ics = ics.replace("TZID=Central Europe Standard Time", "TZID=Europe/Berlin")
ics = ics.replace("TZID:Central Europe Standard Time", "TZID=Europe/Berlin")

# UTC-Zeiten umwandeln in TZID=Europe/Berlin
def convert_utc_line(match):
    key = match.group(1)
    time_str = match.group(2)
    utc_dt = datetime.strptime(time_str, "%Y%m%dT%H%M%SZ").replace(tzinfo=pytz.utc)
    berlin_dt = utc_dt.astimezone(BERLIN_TZ)
    return f"{key};TZID=Europe/Berlin:{berlin_dt.strftime('%Y%m%dT%H%M%S')}"

ics = re.sub(r"(DTSTART|DTEND|RECURRENCE-ID):(\d{8}T\d{6})Z", convert_utc_line, ics)

# Neue Datei schreiben
with open("reachcalendar_converted.ics", "w", encoding="utf-8") as f:
    f.write(ics)
