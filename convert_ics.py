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

# Entferne VTIMEZONE-Blöcke
ics = re.sub(r"BEGIN:VTIMEZONE.*?END:VTIMEZONE\r?\n", "", ics, flags=re.DOTALL)

# Ersetze Microsoft-Zeitzonen
ics = ics.replace("TZID=W. Europe Standard Time", "TZID=Europe/Berlin")
ics = ics.replace("TZID:W. Europe Standard Time", "TZID=Europe/Berlin")
ics = ics.replace("TZID=Central Europe Standard Time", "TZID=Europe/Berlin")
ics = ics.replace("TZID:Central Europe Standard Time", "TZID=Europe/Berlin")

# UTC-Zeitstempel konvertieren
def convert_utc(match):
    field = match.group(1)
    dt = datetime.strptime(match.group(2), "%Y%m%dT%H%M%SZ")
    dt += timedelta(hours=1)
    return f"{field};TZID=Europe/Berlin:{dt.strftime('%Y%m%dT%H%M%S')}"

ics = re.sub(r"(DTSTART|DTEND|RECURRENCE-ID):(\d{8}T\d{6})Z", convert_utc, ics)

# Google-kompatiblen VTIMEZONE-Block einfügen
vtimezone_block = """
BEGIN:VTIMEZONE
TZID:Europe/Berlin
X-LIC-LOCATION:Europe/Berlin
BEGIN:DAYLIGHT
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
TZNAME:GMT+2
DTSTART:19700329T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
TZNAME:GMT+1
DTSTART:19701025T030000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
END:STANDARD
END:VTIMEZONE
"""
ics = ics.replace("BEGIN:VCALENDAR", "BEGIN:VCALENDAR\n" + vtimezone_block.strip())

# Datei speichern
with open(converted_path, "w", encoding="utf-8") as f:
    f.write(ics)
