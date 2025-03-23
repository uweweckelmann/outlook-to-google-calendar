import requests
import re
from datetime import datetime, timedelta
import pytz

# 📥 URL deiner Original-ICS-Datei
OUTLOOK_ICS_URL = 'https://outlook.office365.com/owa/calendar/1f33ba88713f4be89407aa4efcafbbc0@svwestfalen.de/4d297caa680842f495fe97af6ea95ede15552394813414379089/S-1-8-939608001-31717856-4038653985-2387835883/reachcalendar.ics'

# 🌍 Zeitzonen
BERLIN_TZ = pytz.timezone('Europe/Berlin')

def convert_utc_to_berlin(dt_str):
    """Konvertiert UTC Zeitstring (YYYYMMDDTHHMMSS) zu Berlin Zeit ohne Z."""
    utc_dt = datetime.strptime(dt_str, '%Y%m%dT%H%M%S')
    utc_dt = utc_dt.replace(tzinfo=pytz.utc)
    berlin_dt = utc_dt.astimezone(BERLIN_TZ)
    return berlin_dt.strftime('%Y%m%dT%H%M%S')

def main():
    # 🔄 ICS-Datei abrufen
    response = requests.get(OUTLOOK_ICS_URL)
    ics = response.text

    new_lines = []

    for line in ics.splitlines():
        # ⛔️ Entferne VTIMEZONE-Blöcke (Microsoft-Spezial)
        if line.startswith("BEGIN:VTIMEZONE") or line.startswith("END:VTIMEZONE"):
            continue
        if "TZID:Central Europe Standard Time" in line or "TZID:W. Europe Standard Time" in line:
            line = line.replace("TZID=Central Europe Standard Time", "TZID=Europe/Berlin")
            line = line.replace("TZID=W. Europe Standard Time", "TZID=Europe/Berlin")

        # ✅ UTC -> Europe/Berlin konvertieren
        if re.match(r"(DTSTART|DTEND|RECURRENCE-ID):\d{8}T\d{6}Z", line):
            field, dtstr = line.split(":")
            berlin_dt = convert_utc_to_berlin(dtstr[:-1])  # 'Z' abschneiden
            new_lines.append(f"{field};TZID=Europe/Berlin:{berlin_dt}")
        else:
            new_lines.append(line)

    # 💾 Neue Datei schreiben
    with open("reachcalendar_converted.ics", "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

if __name__ == '__main__':
    main()
