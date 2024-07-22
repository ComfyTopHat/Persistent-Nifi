from nifi_manager import NifiManager
import time

connected = False
NIFI_PASSWORD = ""
NIFI_USERNAME = ""
NIFI_HOSTNAME = ""
NIFI_REGISTRY_HOSTNAME = ""
while not (connected):
    try:
        nm = NifiManager(NIFI_HOSTNAME, NIFI_REGISTRY_HOSTNAME, NIFI_USERNAME, NIFI_PASSWORD)
        ## Once the API is up, give it 30 seconds to finish booting
        time.sleep(30)
        connected = True
    except:
        print("Waiting for Nifi application to launch")
        time.sleep(10)
nm.initialize_template_from_registry()