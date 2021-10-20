from pyngrok import ngrok,conf
# Open a HTTP tunnel on the default port 80
# <NgrokTunnel: "http://<public_sub>.ngrok.io" -> "http://localhost:80">
def log_event_callback(log):
    print(str(log))

conf.get_default().log_event_callback = log_event_callback
# http_tunnel = ngrok.connect("file:///C:/Users/LDLuc/Pictures/final_thesis/path/",bind_tls=True)
# tunnels = ngrok.get_tunnels()
# print(tunnels)

import json
import pandas as pd

request1 = '''
{
  "detectIntentResponseId": "85bc43eb-aa05-4eb3-9edf-3906a4bea2c9",
  "intentInfo": {
    "lastMatchedIntent": "projects/maximal-emitter-279708/locations/us-east1/agents/6b21725c-c625-42dc-ad10-2ffe08a4f769/intents/fc2593aa-e492-41fb-8174-dd1d31425980",
    "displayName": "recommendation",
    "confidence": 1.0
  },
  "pageInfo": {
    "currentPage": "projects/maximal-emitter-279708/locations/us-east1/agents/6b21725c-c625-42dc-ad10-2ffe08a4f769/flows/00000000-0000-0000-0000-000000000000/pages/93c41165-72b8-4160-852f-b2a2e1bd2063",
    "formInfo": {}
  },
  "sessionInfo": {
    "session": "projects/maximal-emitter-279708/locations/us-east1/agents/6b21725c-c625-42dc-ad10-2ffe08a4f769/sessions/dfMessenger-58641064:detectIntent",
    "parameters": {
      "exhibition": "King Caspar"
    }
  },
  "fulfillmentInfo": {
    "tag": "recommendation"
  },
  "messages": [
    {
      "text": {
        "text": [
          "Maybe you are also interested in this."
        ],
        "redactedText": [
          "Maybe you are also interested in this."
        ]
      },
      "responseType": "HANDLER_PROMPT",
      "source": "VIRTUAL_AGENT"
    }
  ],
  "text": "Show me similar exhibits.",
  "languageCode": "en"
}
'''
request2 = '''
{
  "detectIntentResponseId": "65cab722-513c-4c46-b071-9c3dd1cd4e21",
  "intentInfo": {
    "lastMatchedIntent": "projects/maximal-emitter-279708/locations/us-east1/agents/6b21725c-c625-42dc-ad10-2ffe08a4f769/intents/6fe8042f-7d9d-4324-9383-9f46a245c885",
    "parameters": {
      "exhibition": {
        "originalValue": "King Caspar",
        "resolvedValue": "King Caspar"
      }
    },
    "displayName": "Exhibition_Item",
    "confidence": 1.0
  },
  "pageInfo": {
    "currentPage": "projects/maximal-emitter-279708/locations/us-east1/agents/6b21725c-c625-42dc-ad10-2ffe08a4f769/flows/00000000-0000-0000-0000-000000000000/pages/c0070de9-0c7a-4f1e-b90a-0987d83b4a81",
    "formInfo": {}
  },
  "sessionInfo": {
    "session": "projects/maximal-emitter-279708/locations/us-east1/agents/6b21725c-c625-42dc-ad10-2ffe08a4f769/sessions/dfMessenger-58641064:detectIntent",
    "parameters": {
      "exhibition": "King Caspar"
    }
  },
  "fulfillmentInfo": {
    "tag": "Exhibition_Item"
  },
  "text": "King Caspar",
  "languageCode": "en"
}'''
data1 = json.loads(request1)
data2 = json.loads(request2)
df = pd.json_normalize(data1,record_path = ['messages'],
                       meta=[['intentInfo','displayName'],
                             ['intentInfo','confidence'],
                             # ['intentInfo','parameters'],
                             ['sessionInfo','parameters'],
                             ['fulfillmentInfo','tag'],
                             'text'])
df_empty = pd.DataFrame(columns = ['session','exhibit_checked','exhibit_unchecked','preference'])

def transfer_request_to_dict(request_json,returned_entity):
    '''
    here to store the interaction between dialogflow and end user, we save part of the information in requests from dialogflow
    and the returned entity from webhook to the dialogflow as a dataframe and update these information.
    :param request_json: the request sent from dialogflow
    :param returned_entity: the returned entity from webhook service
    :return:
    '''
    d = {}
    # if "fulfillmentResponse" in request_json.keys():
    #     d["fulfillment_response"] = request_json["fulfillmentResponse"]
    if "intentInfo" in request_json.keys():
        if 'displayName' in request_json['intentInfo'].keys():
            d["intentInfo.displayName"] = request_json["intentInfo"]['displayName']
            d["intentInfo.confidence"] = request_json["intentInfo"]['confidence']
        if 'parameters' in request_json['intentInfo'].keys():
            d["intentInfo.parameters.type"] = request_json["intentInfo"]['parameters'].keys()
            d['intentInfo.parameters.originalValue'] = [ request_json["intentInfo"]['parameters'][i]["originalValue"] for i in request_json["intentInfo"]['parameters'].keys()]
            d['intentInfo.parameters.resolvedValue'] = [ request_json["intentInfo"]['parameters'][i]["resolvedValue"] for i in request_json["intentInfo"]['parameters'].keys()]
    if "sessionInfo" in request_json.keys():
        if 'session' in request_json['sessionInfo'].keys():
            d['sessionInfo.session'] = request_json['sessionInfo']['session'].split('/')[-1] # get the session id
        if 'parameters' in request_json['sessionInfo'].keys():
            d['sessionInfo.parameters.type'] = request_json['sessionInfo']['parameters'].keys()
            d['sessionInfo.parameters.value'] = [request_json["sessionInfo"]['parameters'][i] for
                                                        i in request_json["sessionInfo"]['parameters'].keys()]
    if 'fulfillmentInfo' in request_json.keys():
        if 'tag' in request_json['fulfillmentInfo'].keys():
            d["fulfillmentInfo.tag"] = request_json["fulfillmentInfo"]['tag']
    if 'text' in request_json.keys():
        d['text'] = request_json['text']



