import requests

class NifiManager():
    def __init__(self, nifiAddress, registryAddress, nifiUser, nifiPass):
        self.localNifiAddress = nifiAddress
        self.localRegistryAddress = registryAddress
        print("Retrieving JWT from: " + self.localNifiAddress)
        self.jwt = NifiManager.get_nifi_jwt(self.localNifiAddress, nifiUser, nifiPass)


    def initialize_template_from_registry(self):
        self.add_nifi_registry()
        nifiId = self.pull_process_group_from_registry()
        self.start_nifi_process_group(nifiId)


    def filter_templates(payloadJson, templateName):
        for template in payloadJson:
            if template["template"]["name"] == templateName:
                return {"id" : template["template"]["id"],
                        "groupId" : template["template"]["groupId"]}

    def get_process_group_details(self):
        headers = {'Content-type': 'application/json',
            "Authorization" : self.jwt,
            'Host': '127.0.0.1'}
        resp = requests.get("https://" + self.localNifiAddress + "/nifi-api/flow/registries/",
                            headers=headers,   
                            verify=False)
        print("REGISTRIES Response: " + resp.text)
        registryId = resp.json()["registries"][0]["registry"]["id"]
        print("REGISTRY ID: " + registryId)
        resp = requests.get("https://" + self.localNifiAddress + "/nifi-api/flow/registries/" + registryId + "/buckets",
                            headers=headers,       
                            verify=False)
        print("RESPONSE FROM GETTING BUCKETS: " + resp.text)
        bucketId = resp.json()["buckets"][0]["id"]
        print("BUCKET ID: " + bucketId)
        resp = requests.get("https://" + self.localNifiAddress + "/nifi-api/flow/registries/" + registryId + "/buckets/" + bucketId + "/flows",
                            headers=headers,
                            verify=False)
        flowId = resp.json()["versionedFlows"][0]["versionedFlow"]["flowId"]
        resp = requests.get("https://" + self.localNifiAddress + "/nifi-api/flow/process-groups/root",
                            headers=headers,       
                            verify=False)
        processGroupId = resp.json()["processGroupFlow"]["id"]
        return {
            "registryId" : registryId,
            "bucketId" : bucketId,
            "flowId" : flowId,
            "processGroupId" : processGroupId
        }

    @staticmethod
    def get_nifi_jwt(localNifiAddress, username, password):
        payload = {
        "username" : username,
        "password" : password
        }
        
        resp = requests.post("https://" + localNifiAddress + "/nifi-api/access/token",
                            data=payload,
                            headers={'Host': '127.0.0.1'},
                            verify=False)
        token ="Bearer " + resp.text
        return token



    ###### Add the local registry to Nifi instance
    def add_nifi_registry(self):
        payload = {
            "revision": {
                "version": 0
            },
            "disconnectedNodeAcknowledged": False,
            "component": {
                "name": "Local Registry",
                "description": "",
                "properties" :{ "url" : "http://" + self.localRegistryAddress },  
                "type": "org.apache.nifi.registry.flow.NifiRegistryFlowRegistryClient"
            }
        }

        headers = {'Content-type': 'application/json',
                "Authorization" : self.jwt,
                'Host': '127.0.0.1'}
        url = "https://" + self.localNifiAddress + "/nifi-api/controller/registry-clients"
        resp = requests.post(url=url,
                            headers=headers,
                            json=payload,
                            verify=False)


    def pull_process_group_from_registry(self):
        ###### Pull the process group from the registry
        processGroup = self.get_process_group_details()
        payload = {
        "revision": {
            "version": 0
        },
        "disconnectedNodeAcknowledged": False,
        "component": {
            "position": {
            "x": 371,
            "y": 83.00231170654297
            },
            "versionControlInformation": {
            "registryId": processGroup["registryId"],
            "bucketId": processGroup["bucketId"],
            "flowId": processGroup["flowId"],
            "version": 1
            }
        }
        }
        headers = {'Content-type': 'application/json',
                "Authorization" : self.jwt,
                'Host': '127.0.0.1'}

        url = "https://" + self.localNifiAddress + "/nifi-api/process-groups/" + processGroup["processGroupId"] +"/process-groups?parameterContextHandlingStrategy=KEEP_EXISTING"
        resp = requests.post(url=url,
                            headers=headers,
                            json=payload,
                            verify=False)

        id = resp.json()["component"]["id"]
        return id

    def start_nifi_process_group(self,id):
        ###### Start the process group
        payload = {
            "id" : id,
            "state" : "RUNNING"
        }
        headers = {'Content-type': 'application/json',
            "Authorization" : self.jwt,
            'Host': '127.0.0.1'}
        resp = requests.put("https://" + self.localNifiAddress + "/nifi-api/flow/process-groups/" + id,
                            verify=False,
                            headers=headers,
                            json=payload
        )