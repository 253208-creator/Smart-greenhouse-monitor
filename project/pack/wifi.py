import network
import urequests
import wifi_utils
SSID = "UREL-SC661-V-2.4G"
PSWD = "TomFryza"
THINGSPEAK_WRITE_API_KEY = "M3DCB3HGAEOAUFTL"

API_URL = "https://api.thingspeak.com/update"

class WiFiThingSpeak:
    def __init__(self, url=API_URL):
        self.url = url
        self.wifi = network.WLAN(network.STA_IF)

    def ensure_connected(self):
        if self.wifi.isconnected():
            return True
        return wifi_utils.connect(self.wifi, SSID, PSWD)

    def send(self, field1=None, field2=None, field3=None):
        if not self.ensure_connected():
            print("Wi-Fi not connected; upload skipped.")
            return False

        parts = [f"api_key={THINGSPEAK_WRITE_API_KEY}"]
        if field1 is not None:
            parts.append(f"field1={field1}")
        if field2 is not None:
            parts.append(f"field2={field2}")
        if field3 is not None:
            parts.append(f"field3={field3}")

        body = "&".join(parts)
        response = None
        try:
            response = urequests.post(
                self.url,
                data=body,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            entry = response.text.strip()
            ok = response.status_code == 200 and entry != "0"
            print(f"ThingSpeak status={response.status_code} entry={entry} ok={ok}")
            return ok
        except Exception as err:
            print("Upload failed:", err)
            return False
        finally:
            if response is not None:
                response.close()

    def disconnect(self):
        wifi_utils.disconnect(self.wifi)