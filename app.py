# import flask dependencies
from flask import Flask, request, jsonify,render_template
from graph_database import ArtGraph
from component.reply_pattern import reply_pattern
from embedding import get_similarity
import random
# initialize the flask app
app = Flask(__name__)

# default route
@app.route('/')
def index():
    return render_template("index.html")


# function for responses
def results():
    # build a request object
    req = request.get_json(force=True)
    print(req)
    # fetch action from json
    # action = req.get('queryResult').get('action')

    # return a fulfillment response
    return {'fulfillment_response': {'messages':[{'text':'This is a response from webhook.'}], 'merge_behavior':'MERGE_BEHAVIOR_UNSPECIFIED'}}

# create a route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
# @app.route('/webhook')

def webhook():

    tag = request.json['fulfillmentInfo']['tag']
    exhibit = request.json['intentInfo']['parameters']['exhibition']['resolvedValue']
    fulfillmentResponse = {
        'fulfillment_response': {
            'messages': [{
            'payload':
                {
                    "richContent": [
                        [
                            {
                                "type": "image",
                                "rawUrl": "https://www.planetware.com/wpimages/2020/02/france-in-pictures-beautiful-places-to-photograph-eiffel-tower.jpg",
                                "accessibilityText": "Dialogflow across platforms"
                            },
                            {
                                "type": "info",
                                "title": "Dialogflow",
                                "subtitle": "Build natural and rich conversational experiences",
                                "actionLink": "https://cloud.google.com/dialogflow/docs"
                            },
                            {
                                "type": "chips",
                                "options": [
                                    {
                                        "text": "Case Studies",
                                        "link": "https://cloud.google.com/dialogflow/case-studies"
                                    },
                                    {
                                        "text": "Docs",
                                        "link": "https://cloud.google.com/dialogflow/docs"
                                    }
                                ]
                            }
                        ]
                    ]
                }
        # {
        #   "richContent": [
        #     [
        #         {
        #             "type": "image",
        #             "rawUrl": "https://www.wikidata.org/wiki/Q61890089#/media/File:Rembrandt-drawing-two-drummers-british-museum.jpg",
        #             "accessibilityText": "Dialogflow across platforms"
        #         },
        #       {
        #         "type": "info",
        #         "title": "Info item title",
        #         "subtitle": "Info item subtitle",
        #         "actionLink": "https://www.wikidata.org/wiki/Q61890089"
        #       }
        #     ]
        #   ]
        # }
        }
        ]
    },
    }
    return jsonify(fulfillmentResponse)

@app.route('/exhibit', methods=['GET', 'POST'])
# @app.route('/webhook')

def exhibit():
    # An example of the request json file
    '''
    {
  "detectIntentResponseId": "61065ca1-2810-41c3-9fde-a0020c4e754a",
  "intentInfo": {
    "lastMatchedIntent": "projects/maximal-emitter-279708/locations/us-east1/agents/6b21725c-c625-42dc-ad10-2ffe08a4f769/intents/6fe8042f-7d9d-4324-9383-9f46a245c885",
    "parameters": {
      "exhibition": {
        "originalValue": "Two Dummers",
        "resolvedValue": "Two Drummers"
      }
    },
    "displayName": "Exhibition_Item",
    "confidence": 1.0
  },
  "pageInfo": {
    "currentPage": "projects/maximal-emitter-279708/locations/us-east1/agents/6b21725c-c625-42dc-ad10-2ffe08a4f769/flows/00000000-0000-0000-0000-000000000000/pages/dc1e9e70-d64b-48da-99d4-2580d9f0bcdf",
    "formInfo": {}
  },
  "sessionInfo": {
    "session": "projects/maximal-emitter-279708/locations/us-east1/agents/6b21725c-c625-42dc-ad10-2ffe08a4f769/sessions/de8870-120-371-cc9-a45795b68",
    "parameters": {
      "exhibition": "Two Drummers"
    }
  },
  "fulfillmentInfo": {
    "tag": "Exhibit"
  },
  "text": "Two Dummers",
  "languageCode": "en"
}
    :return:
    '''
    # here we should check the confidence
    # if request.json['intentInfo']['confidence'] > 0.5 and /
    # request.json['intentInfo']['displayName'] == 'Exhibition_Item'

    # what if there is multiple exhibit?
    print(request.json)
    tag = request.json['intentInfo']['displayName']
    tag_fullfillment = request.json['fulfillmentInfo']['tag']
    print(tag,tag_fullfillment)
    if tag == 'Exhibition_Item':
        exhibit_resolvedvalue = request.json['intentInfo']['parameters']['exhibition']['resolvedValue']
        data = handler.show_exhibit(exhibit_resolvedvalue)
        handler.update_exhibit(exhibit_resolvedvalue)
        print(handler.preference)
        if data == None:
            fulfillmentResponse = {'fulfillment_response': {'messages':[{'text':'Sorry, there is no such exhibits you desired in my knowledge.'}], 'merge_behavior':'MERGE_BEHAVIOR_UNSPECIFIED'}}

            return jsonify(fulfillmentResponse)
        else:
            name = data[0]['n']['name']
            picture_url = data[0]['n']['img']
            wiki_uri = data[0]['n']['uri']
            des =  data[0]['n']['description']
            fulfillmentResponse = {
                'fulfillment_response': {
                    'messages': [{
                        'payload':
                            {
                                "richContent": [
                                    [
                                        {
                                            "type": "image",
                                            "rawUrl": picture_url,
                                            "accessibilityText": name
                                        },
                                        {
                                            "type": "info",
                                            "title": name,
                                            "subtitle": des,
                                            "actionLink": wiki_uri
                                        }
                                        # ,
                                        # {
                                        #     "type": "chips",
                                        #     "options": [
                                        #         {
                                        #             "text": "Case Studies",
                                        #             "link": "https://cloud.google.com/dialogflow/case-studies"
                                        #         },
                                        #         {
                                        #             "text": "Docs",
                                        #             "link": "https://cloud.google.com/dialogflow/docs"
                                        #         }
                                        #     ]
                                        # }
                                    ]
                                ]
                            }

                    }
                    ]
                },
            }
            return jsonify(fulfillmentResponse)
    elif tag == 'Paintings_item':
        exhibit_resolvedvalue = request.json['intentInfo']['parameters']['paintings']['resolvedValue'].replace('\n','')
        print(exhibit)
        handler.update_user_preference(exhibit_resolvedvalue)
        print(handler.preference)
        data = handler.show_exhibit(exhibit_resolvedvalue)
        print(data)
        if data == None:
            fulfillmentResponse = {'fulfillment_response': {
                'messages': [{'text': 'Sorry, there is no such exhibits you desired in my knowledge.'}],
                'merge_behavior': 'MERGE_BEHAVIOR_UNSPECIFIED'}}

            return jsonify(fulfillmentResponse)
        else:
            name = data[0]['n']['name']
            picture_url = data[0]['n']['img']
            wiki_uri = data[0]['n']['uri']
            des = data[0]['n']['description']
            fulfillmentResponse = {
                'fulfillment_response': {
                    'messages': [{
                        'payload':
                            {
                                "richContent": [
                                    [
                                        {
                                            "type": "image",
                                            "rawUrl": picture_url,
                                            "accessibilityText": name
                                        },
                                        {
                                            "type": "info",
                                            "title": name,
                                            "subtitle": des,
                                            "actionLink": wiki_uri
                                        }
                                        # ,
                                        # {
                                        #     "type": "chips",
                                        #     "options": [
                                        #         {
                                        #             "text": "Case Studies",
                                        #             "link": "https://cloud.google.com/dialogflow/case-studies"
                                        #         },
                                        #         {
                                        #             "text": "Docs",
                                        #             "link": "https://cloud.google.com/dialogflow/docs"
                                        #         }
                                        #     ]
                                        # }
                                    ]
                                ]
                            }

                    }
                    ]
                },
            }
            return jsonify(fulfillmentResponse)
    elif tag_fullfillment == 'exhibit_sotry':
        exhibit_resolvedvalue = request.json['sessionInfo']['parameters']['exhibition'].replace('\n', '')
        print(exhibit_resolvedvalue)

        data = handler.show_exhibit(exhibit_resolvedvalue)
        print(data)
        name = data[0]['n']['name']


        story = [i for i in data[0]['n']['exhibit'].split('\n')]
        fulfillmentResponse = {
            'fulfillment_response': {
                'messages': [{
                    'payload':
                        {
                            "richContent": [
                            [
                              {
                                "type": "description",
                                "title": name,
                                "text": story
                              }
                            ]
                          ]
                        }

                }
                ]
            },
        }
        return jsonify(fulfillmentResponse)
    else:
        return jsonify({'fulfillment_response': {
                'messages': [{'text': 'Sorry, there is no such exhibits you desired in my knowledge.'}],
                'merge_behavior': 'MERGE_BEHAVIOR_UNSPECIFIED'}})

@app.route('/questions', methods=['GET', 'POST'])

def questions():

    print(request.json)
    tag = request.json['intentInfo']['displayName']
    if tag =='answer_question':
        # first, if this question is with some parameters
        if 'parameters' in request.json['intentInfo']:
            parameters_dic = request.json['intentInfo']['parameters']
            # caution:
            # here we only consider one type of parameter
            key_para = list(parameters_dic.keys())[0]
            originalValue = parameters_dic[key_para]['originalValue']
            resolvedValue = parameters_dic[key_para]['resolvedValue']
            handler.update_user_preference(resolvedValue)
            print("preference is",handler.preference)
            question = request.json['text'].replace(originalValue,resolvedValue)
            print('question is :',question)
            data = handler.classifier.classify(question)
            print('classified question is:', data)
            answer = handler.answer_prettify(data)
            print('answer is',answer)
            response = reply_pattern(answer,type='answer',question_types = data)
            print(response)
            return jsonify(response)

        # question without parameters, so there should be coreference
        else:
            # here we use the parameters exist in the session
            parameters_dic = request.json['sessionInfo']['parameters']
            key_para = list(parameters_dic.keys())[0]
            for key, value in parameters_dic.items():
                question = request.json['text'] +' '+ value
                print('question is :',question)
                break
            data = handler.classifier.classify(question)
            print('classified question is:', data)
            answer = handler.answer_prettify(data)
            print('answer is',answer)
            response = reply_pattern(answer,type='answer',question_types = data)
            return jsonify(response)
    elif tag == "suggest_question" or request.json['fulfillmentInfo']['tag'] == "suggest_question":
        print("Suggest question mode"+'='*10)
        if 'parameters' in request.json['sessionInfo']:
            parameters_dic = request.json['sessionInfo']['parameters']
            key_para = list(parameters_dic.keys())[0]
            parameter = parameters_dic[key_para]
            print("parameter is: ", parameter)
            # if the parameter here is exhibits or paintings
            if key_para =='exhibition' or key_para=='paintings':
                para_type = 'Paintings' # the type name for search

                neighbors_entity_list = handler.get_neighbors(parameter, type=para_type)
                # properties_list = handler.get_properties(parameter,type=para_type)

                response = reply_pattern(neighbors_entity_list, type='suggest_question', parameter = parameter)
                print(response)
                print("Suggest question mode end" + '=' * 10)
                return jsonify(response)
            # label_preference = handler.decide_label_preference('suggest_question')





@app.route('/recommendation', methods=['GET', 'POST'])

def recommendation():
    print(request.json)
    parameters_dic = request.json['sessionInfo']['parameters']
    key_para = list(parameters_dic.keys())[0]
    parameter = parameters_dic[key_para]
    print("parameter is: ", parameter)
    label_preference = handler.decide_label_preference('recommendation')
    print(label_preference)
    suggest_nodeid = get_similarity(parameter,label=label_preference)

    # handler = ArtGraph()
    data = handler.search_by_nodeId(suggest_nodeid)
    print("the data we got is :", data)
    name = data[0]['n']['name']
    description = data[0]['n']['description']
    uri = data[0]['n']['uri']
    try:
        print("with image")
        img = data[0]['n']['img']
        print(img)
        fulfillmentResponse = {
            'fulfillment_response': {
                'messages': [{
                    'payload':
                        {
                            "richContent": [
                                [
                                    {
                                        "type": "image",
                                        "rawUrl": img,
                                        "accessibilityText": name
                                    },
                                    {
                                        "type": "info",
                                        "title": name,
                                        "subtitle": description,
                                        "actionLink":uri
                                    }

                                ]
                            ]
                        }

                }
                ]
            },
        }
        return jsonify(fulfillmentResponse)
    except:
        print("without image")
        fulfillmentResponse = {
            'fulfillment_response': {
                'messages': [{
                    'payload':
                        {
                            "richContent": [
                                [
                                    # {
                                    #     "type": "image",
                                    #     "rawUrl": img
                                    # },
                                    {
                                        "type": "info",
                                        "title": name,
                                        "subtitle": description,
                                        "actionLink": uri
                                    }

                                ]
                            ]
                        }

                }
                ]
            },
        }
        return jsonify(fulfillmentResponse)
# run the app
if __name__ == '__main__':
    # model = user_model()
    handler = ArtGraph()

    app.run()