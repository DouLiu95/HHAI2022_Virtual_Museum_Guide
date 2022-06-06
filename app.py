# import flask dependencies
from flask import Flask, request, jsonify,render_template
from graph_database import ArtGraph
import graph_database_es
from component.reply_pattern import reply_pattern,connection_pattern
import component.reply_pattern_es as reply_pattern_es
from embedding import get_similarity
import embedding_es
from graph_update import draw_graph
import pandas as pd
import random
# initialize the flask app
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
# default route
@app.route('/')
def index():
    return render_template("neovis.html")
@app.route('/web', methods=['GET', 'POST'])
def web():
    return render_template("file.html")

# function for responses
def results():
    # build a request object
    req = request.get_json(force=True)
    print(req)
    # fetch action from json
    # action = req.get('queryResult').get('action')

    # return a fulfillment response
    return {'fulfillment_response': {'messages':[{'text':'This is a response from webhook.'}], 'merge_behavior':'MERGE_BEHAVIOR_UNSPECIFIED'}}


@app.route('/bot4museum',methods=['POST'])
def bot4museum():
    req = request.get_json()
    print("request is ",req)
    intent = req["queryResult"]["intent"]["displayName"]
    action = req["queryResult"]["action"]
    session = req['session']
    print("="*15+'New Input' + '=*15')
    print("The intent is", intent, "\n The action is ", action)
    # deal with asking for a painting
    if intent == 'description.painting':

        if action == 'painting.entity':
        # action: painting.entity

            # get the Q-uri of the entity in the sentence
            entity_uri = req["queryResult"]["parameters"]["Painting"]

            print("Now is looking for: ", entity_uri)
            if entity_uri.startswith('Q'):
                entity_full_uri = r"http://www.wikidata.org/entity/" + entity_uri
            print("Now is looking for: ", entity_uri)
            handler_es.transfer_request_to_dict(req, returned_entity =entity_full_uri)

            data = handler_es.show_exhibit(entity_uri)
            print("Retrived data is: ",data)
            if data == None:
                fulfillmentResponse = {
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [
                                "Sorry, we can not find the entity you mentioned. Maybe try another name."
                            ]
                        }
                    }
                ]
                }
                print('Not result found for painting.entity')
                return fulfillmentResponse
            else:
                if 'exhibit' in data[0]['n'].keys():
                    # name = data[0]['n']['name']
                    # picture_url = data[0]['n']['img']
                    # wiki_uri = data[0]['n']['uri']
                    # des = data[0]['n']['description']
                    story = data[0]['n']['exhibit']
                    testResponse = {
                        "fulfillmentMessages": [
                                {
                                    "text": {
                                        "text": [
                                            story
                                        ]
                                    }
                                },{
                                    "text": {
                                        "text": [
                                            "Do you want to know more about the exhibit or continue the visiting?"

                                        ]
                                    }
                                },
                            {
                              "payload": {
                                "richContent": [
                                  [
                                    {
                                      "options": [
                                        {
                                          "text": "Continue visiting"
                                        },
                                        {
                                          "text": "I want to ask questions"
                                        },
                                        {
                                          "text": "Show me similar exhibits"
                                        }
                                      ],
                                      "type": "chips"
                                    }
                                  ]
                                ]
                              }
                            }
                        ]
                    }
                    return testResponse
                else:
                    name = data[0]['n']['name']
                    picture_url = data[0]['n']['img']
                    wiki_uri = data[0]['n']['uri']
                    des = data[0]['n']['description']

                    testResponse = {
                        'fulfillmentMessages': [{
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

                                        ]
                                    ]
                                }

                        }
                        ]
                    }

                    return testResponse

    elif intent == 'question.answering':
        parameters_dic = req['queryResult']['parameters']
        output_context_parameters_dic = req['queryResult']['outputContexts'][0]['parameters']

        key_para = [ key for key in parameters_dic.keys() if parameters_dic[key] != '']


        entity_uri = [parameters_dic[key] for key in parameters_dic.keys() if parameters_dic[key] != '']
        handler_es.transfer_request_to_dict(req, entity_uri)

        question = req['queryResult']['queryText']
        for key in key_para:
            output_context_key = key+'.original'
            question = question.replace(output_context_parameters_dic[output_context_key],parameters_dic[key])
        print('question is', question)
        data = handler_es.classifier.classify(question)
        print('classified question is:', data)
        answer = handler_es.answer_prettify(data)
        print('answer is', answer)
        # when no answer is found for the question
        if answer == []:
            fulfillmentResponse = {
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [
                                "Sorry, I can not find that in my knowledge currently, maybe try another question?"
                            ]
                        }
                    }
                ]
            }
            return fulfillmentResponse
        # if found the answer
        response = reply_pattern_es.reply_pattern(answer, type='answer', question_types=data)
        print(response)
        return response
    elif intent == 'Recommendation' or intent == "recommend.another":

        # avoid recommending entities repetitively
        exception = handler_es.history[handler_es.history['session'].isin([session])][
            'response.entity'].to_list()  # here we record the previous recommended items
        # here we include the session intent parameters to the exception
        # for intent in handler.history[handler.history['sessionInfo.session'].isin([session])]['intentInfo.parameters.resolvedValue'].to_list():
        #     if intent != None:
        #         for i in intent:
        #             exception.append(i)
        print(exception)

        # here we record the last intent parameter as current entity, which is the entity user searched
        current_entity = handler_es.history[handler_es.history['session'].isin([session])][
            'parameters'].to_list()
        print("current is ", current_entity)
        parameter = ''
        for i in reversed(current_entity):
            if isinstance(i, list):
                if i != []:
                    parameter = i[0].replace('\n', '')
                    break

        # parameters_dic = request.json['sessionInfo']['parameters']
        # key_para = list(parameters_dic.keys())[0]
        # parameter = parameters_dic[key_para]
        print("parameter is: ", parameter, 'the type of parameter is {}'.format(type(parameter)))
        if  'exhibit' in req["queryResult"]['queryText'] or 'painting' in req["queryResult"]['queryText']:
            label_preference = 'Exhibit'
        else:
            label_preference = handler_es.decide_label_preference('recommendation', session)
        print('prefered label is', label_preference)
        current_nodeid, suggest_nodeid = embedding_es.get_similarity(parameter, label='Exhibit', exception_list=exception)

        # handler_es = ArtGraph()
        current_data = handler_es.search_by_nodeId(current_nodeid)
        data = handler_es.search_by_nodeId(suggest_nodeid)
        current_uri = current_data[0]['n']['uri']
        print("the data we got is :", data)
        name = data[0]['n']['name']
        description = data[0]['n']['description']
        uri = data[0]['n']['uri']
        query_for_graph = draw_graph(uri1=current_uri, uri2=uri).replace('RETURN p',
                                                                         "RETURN p as path, NODES(p) as nodes,relationships(p) as rel")
        handler_es.g.run(query_for_graph).data()
        # handler_es.
        handler_es.transfer_request_to_dict(request.json, parameter, uri, query_for_graph)
        print("name is {}\ndesc is {}\nuri is {}\n".format(name, description, uri))
        try:
            print("with image")
            img = data[0]['n']['img']
            print(img)
            fulfillmentResponse = {'fulfillmentMessages': [{
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
                                            "actionLink": uri
                                        },

                                        {
                                            "type": "chips",
                                            "options": [
                                                {
                                                    "text": "Another one"},
                                                {"text": "Why this one?"}

                                            ]
                                        }

                                    ]
                                ]
                            }

                    }
                    ]
                }
            return fulfillmentResponse
        except:
            print("without image")
            fulfillmentResponse = {'fulfillmentMessages': [{
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
                                        },
                                        # {
                                        #     "type": "button",
                                        #     "icon": {
                                        #         "type": "chevron_right",
                                        #         "color": "#FF9800"
                                        #     },
                                        #     "text": "Knowledge Graph",
                                        #     "link": "https://25c7-2a02-a466-ba15-1-985e-cbb1-318-13ae.ngrok.io",
                                        #
                                        # },
                                        {
                                            "type": "chips",
                                            "options": [
                                                {
                                                    "text": "Another one"},
                                                {"text": "Why this one?"}
                                            ]
                                        }

                                    ]
                                ]
                            }

                    }
                    ]
                }
            return fulfillmentResponse

        # if 'parameters' in req['queryResult']:
        #     parameters_dic = request.json['intentInfo']['parameters']
        #     # caution:
        #     # here we only consider one type of parameter
        #     key_para = list(parameters_dic.keys())[0]
        #     originalValue = parameters_dic[key_para]['originalValue']
        #     resolvedValue = parameters_dic[key_para]['resolvedValue']
        #     # handler_es.update_user_preference(resolvedValue) # this method is abandoned
        #     print("preference is",handler_es.preference)
        #     question = request.json['text'].replace(originalValue,resolvedValue)
        #     print('question is :',question)
        #     data = handler_es.classifier.classify(question)
        #     print('classified question is:', data)
        #     answer = handler_es.answer_prettify(data)
        #     print('answer is',answer)
        #     response = reply_pattern(answer,type='answer',question_types = data)
        #     print(response)
        #
        #     handler_es.transfer_request_to_dict(request.json, resolvedValue,answer)
        #
        #     return jsonify(response)

    elif intent == 'question.example' or intent == 'question.another':
        print("Suggest question mode" + '=' * 10)
        current_entity = handler_es.history[handler_es.history['session'].isin([session])][
            'parameters'].to_list()
        print("current is ", current_entity)
        parameter = ''

        for i in reversed(current_entity):
            if isinstance(i, list):
                parameter = i[0].replace('\n', '')
                break
        # parameters_dic = request.json['sessionInfo']['parameters']
        # key_para = list(parameters_dic.keys())[-1]
        # parameter = parameters_dic[key_para].replace('\n', '')
        print("parameter is: ", parameter)
        # if the parameter here is exhibits or paintings
        if parameter in handler_es.Paintings:
            # print('key para is ',key_para)
            para_type = 'Paintings'  # the type name for search

            neighbors_entity_list = handler_es.get_neighbors(parameter, type=para_type)
            # properties_list = handler_es.get_properties(parameter,type=para_type)

            response = reply_pattern_es.reply_pattern(neighbors_entity_list, type='suggest_question', parameter=parameter)
            print(response)
            print("Suggest question mode end" + '=' * 10)
            return jsonify(response)
        else:
            fulfillmentResponse = {
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [
                                "Sorry, please ask one entity first."
                            ]
                        }
                    }
                ]
            }
            print('Not result found for painting.entity')
            return fulfillmentResponse

    elif intent == 'question.attribute' :
        # here is to find another paintings with the same attributes
        # exception_list = handler_es.history[handler_es.history['session'].isin([session])][
        #     'response.entity'].to_list()  # here we record the previous recommended items
        embedding = pd.read_csv("component/export.csv")
        response_list = handler_es.history[handler_es.history['session'].isin([session])][
            'response.entity'].to_list()  # here we record the previous recommended items
        response = []
        for i in response_list:
            if isinstance(i, str):
                response.append(i)
        exception = response
        # for l in exception_list:
        #     if isinstance(l, list):
        #         exception.extend(l)
        # exception = list(set(exception)) + response

        parameters_dic = req['queryResult']['parameters']

        key_para = [key for key in parameters_dic.keys() if parameters_dic[key] != '']

        parameter_list = [parameters_dic[key] for key in parameters_dic.keys() if parameters_dic[key] != '']
        print('parameter_list here is', parameter_list)
        if len(parameter_list) == 0:

            parameter_list = handler.history[handler.history['session'].isin([session])][
                'parameters'].to_list()
            key_list = handler.history[handler.history['session'].isin([session])][
                'parameters_dic'].to_list()
            for i, j in zip(reversed(parameter_list), reversed(key_list)):
                print(i, j)
                if not pd.isna(i):
                    parameter = i[0].replace('\n', '')
                    key = list(j)[-1]
                    break
        else:
            parameter = parameter_list[0]
            key = key_para[0]
        # here add the prefix of the URI
        if parameter.startswith('Q'):
            parameter = r"http://www.wikidata.org/entity/" + parameter
        parameter_name = embedding[embedding['uri'] == parameter]['name'].values[0]
        query = "MATCH (a),  (a)-[]-(b{uri:'" + parameter + "'}) where NOT  a.uri  in" + str(
            exception) + "  RETURN a limit 1"
        data = handler_es.g.run(query).data()

        if data == []:  # there is no such graph
            handler_es.transfer_request_to_dict(req, parameter, Cypher=query)


            fulfillmentResponse = {'fulfillmentMessages': [
                        {
                            "text": {
                                "text": [
                                    "Sorry, after searching in our knowledge base, there is no pianting with this attribute."
                                ]
                            }
                        },
                        {'payload':
                            {'richContent': [[
                                {"type": "chips",
                                 "options": [{"text": 'Another one'}, {"text": 'Stop recommendation'}]}]]}}
                    ]
                }

            return fulfillmentResponse
        else:
            name = data[0]['a']['name']
            des = data[0]['a']['description']
            uri = data[0]['a']['uri']
            handler_es.transfer_request_to_dict(req, parameter, uri, Cypher=query)

            try:
                img = data[0]['a']['img']
            except:
                print("no image for ", name)
                img = ''

            def attribute_to_text(key, parameter):
                if key == 'genre':
                    text = 'It also has ' + parameter + ' as its genre.'
                elif key == 'material':
                    text = 'It also has ' + parameter + ' as its material.'
                elif key == 'movement':
                    text = 'It also belongs to the movement ' + parameter
                elif key == 'keyword':
                    text = 'It also depicts ' + parameter
                elif key == 'collection':
                    text = 'It is also in the ' + parameter
                elif key == 'exhibition':
                    text = 'It is also in the ' + parameter
                elif key == 'creator' or key == 'person':
                    text = 'It is also created by ' + parameter
                return text

            attribute_to_text(key, parameter)
            fulfillmentResponse = {'fulfillmentMessages': [{
                            "text": {
                                "text": [
                                    attribute_to_text(key, parameter_name)
                                ]
                            }
                        },
                        {
                        'payload':
                            {
                                "richContent": [
                                    [{
                                        "type": "image",
                                        "rawUrl": img,
                                        "accessibilityText": name
                                    },
                                        {
                                            "type": "info",
                                            "title": name,
                                            "subtitle": des,
                                            "actionLink": uri
                                        }],
                                    [
                                        {"type": "chips",
                                         "options": [{'text': 'Another related entity'},
                                                     {'text': 'Stop recommendation'}]}]
                                ]
                            }

                    }
                    ]
                }
            return fulfillmentResponse

    elif intent == 'recommend.connection':

        Cypher = handler_es.history[handler_es.history['session'].isin([session])].iloc[-1]['Cypher']
        print('the cypher for connection is ', Cypher)
        # if 'where NOT  a.name' not in Cypher:
        last_entity = handler_es.history[handler_es.history['session'].isin([session])].iloc[-1][
            'response.entity']
        query_data = handler_es.g.run(Cypher).data()

        handler_es.transfer_request_to_dict(req, last_entity)
        print("query_data is", query_data)
        pattern_list, relationship_dic = reply_pattern_es.connection_pattern(query_data)
        if query_data == [] or pattern_list == []:  # there is no such graph
            print('the query data is empty')
            fulfillmentResponse = {'fulfillmentMessages': [{
                        'payload':
                            {
                                "richContent": [[{
                                    "type": "info",
                                    "title": 'Not Found',
                                    "subtitle": "Unfortunately, after searching in our knowledge graph, these two items do not share a common attributes. "

                                },
                                    {"type": "chips",
                                     "options": [{"text": 'Another one'}, {"text": 'Stop recommendation'}]}]]}}
                    ]
                }
            return fulfillmentResponse
        else:
            object_list = []
            for i in relationship_dic:
                object_list.extend(relationship_dic[i])
            object_list_text = []
            for obj in object_list:
                object_list_text.append({"text": obj})
            object_list_text.append({"text": 'Another one'})
            object_list_text.append({"text": 'Stop recommendation'})
            # pattern_list[-1][
            #     'subtitle'] = 'Select a option below to check other paintings with the listed attribute or stop the recommendation.'
            #
            # pattern_list.append({
            #     "type": "button",
            #     "icon": {
            #         "type": "chevron_right",
            #         "color": "#FF9800"
            #     },
            #     "text": "Click to check the Knowledge Graph",
            #     "link": "", # address of api
            #
            # })
            fulfillmentResponse = { 'fulfillmentMessages': [pattern_list,
                                                            {
                                                                "text": {
                                                                    "text": [
                                                                        'Select an option here to check other paintings with the listed attribute or stop the recommendation.'

                                                                    ]
                                                                }
                                                            },
                                                            {
                        'payload':
                            {
                                "richContent": [

                                    [
                                        {"type": "chips",
                                         "options": object_list_text}]

                                ]
                            }

                    }
                    ]
                }
            return fulfillmentResponse
# create a route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
# @app.route('/webhook')

def webhook():

    # tag = request.json['fulfillmentInfo']['tag']
    # exhibit = request.json['intentInfo']['parameters']['exhibition']['resolvedValue']
    fulfillmentResponse = {
          "fulfillmentMessages": [
            {
              "card": {
                "title": "card title",
                "subtitle": "card text",
                "imageUri": "https://example.com/images/example.png",
                "buttons": [
                  {
                    "text": "button text",
                    "postback": "https://example.com/path/for/end-user/to/follow"
                  }
                ]
              }
            }
          ]
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
        handler.transfer_request_to_dict(request.json,exhibit_resolvedvalue)
        # handler.update_exhibit(exhibit_resolvedvalue)
        # print(handler.preference)
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
        handler.transfer_request_to_dict(request.json, exhibit_resolvedvalue)
        # handler.update_user_preference(exhibit_resolvedvalue)
        # print(handler.preference)
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

        if len(data[0]['n']['exhibit'].split(' ')) > 75:
            story = [i for i in data[0]['n']['exhibit'].split('\n')]
            fulfillmentResponse = {
                'fulfillment_response': {
                    'messages': [{
                        'payload':
                            {
                                "richContent": [
                                [
                                  {
                                    "type": "accordion",
                                    "title": name,
                                    "subtitle": "Click to check the background story of {}".format(name),
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
            story = [i for i in data[0]['n']['exhibit'].split('\n')]
            fulfillmentResponse = {
                'fulfillment_response': {
                    'messages': [{
                        'payload':
                            {
                                "richContent": [
                                    [
                                        {
                                            "type": "info",
                                            "title": "The background story of {}".format(name),
                                            # "subtitle": "The background story of {}".format(name),
                                            "subtitle": story
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
            # handler.update_user_preference(resolvedValue) # this method is abandoned
            print("preference is",handler.preference)
            question = request.json['text'].replace(originalValue,resolvedValue)
            print('question is :',question)
            data = handler.classifier.classify(question)
            print('classified question is:', data)
            answer = handler.answer_prettify(data)
            print('answer is',answer)
            response = reply_pattern(answer,type='answer',question_types = data)
            print(response)

            handler.transfer_request_to_dict(request.json, resolvedValue,answer)

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
            handler.transfer_request_to_dict(request.json, parameters_dic.values(),answer)

            return jsonify(response)
    elif tag == "suggest_question" or request.json['fulfillmentInfo']['tag'] == "suggest_question":
        print("Suggest question mode"+'='*10)
        session = request.json['sessionInfo']['session'].split('/')[-1]
        current_entity = handler.history[handler.history['sessionInfo.session'].isin([session])][
            'intentInfo.parameters.resolvedValue'].to_list()
        print("current is ", current_entity)
        for i in reversed(current_entity):
            if isinstance(i, list):
                parameter = i[0].replace('\n', '')
                break
        # parameters_dic = request.json['sessionInfo']['parameters']
        # key_para = list(parameters_dic.keys())[-1]
        # parameter = parameters_dic[key_para].replace('\n', '')
        print("parameter is: ", parameter)
        # if the parameter here is exhibits or paintings
        if parameter in handler.Paintings:
            # print('key para is ',key_para)
            para_type = 'Paintings'  # the type name for search

            neighbors_entity_list = handler.get_neighbors(parameter, type=para_type)
            # properties_list = handler.get_properties(parameter,type=para_type)

            response = reply_pattern(neighbors_entity_list, type='suggest_question', parameter=parameter)
            print(response)
            print("Suggest question mode end" + '=' * 10)
            return jsonify(response)
            # label_preference = handler.decide_label_preference('suggest_question')





@app.route('/recommendation', methods=['GET', 'POST'])

def recommendation():
    print(request.json)
    tag = request.json['fulfillmentInfo']['tag']
    def too_much_recommendation(request):
        # here we check the previous intent, If we find that the user continues to be in the recommended part, we will remind him to continue to visit
        session = request.json['sessionInfo']['session'].split('/')[-1]

        previous_ = handler.history[handler.history['sessionInfo.session'].isin([session])][
            'intentInfo.displayName'].to_list()  # here we record the previous recommended items
        if request.json['intentInfo']['displayName'] == "recommendation.toomuch.negetive" or \
                request.json['intentInfo']['displayName'] == 'recommendation.toomuch.positive' or \
                request.json['intentInfo']['displayName'] == 'recommendation.nomore' or\
            tag == 'attribute' or tag =='end':
            return False
        count = 0

        for intent in reversed(previous_):
            if count>=3:
                return True
            elif 'recommendation.toomuch.negetive' in intent or 'recommendation.toomuch.positive' in intent or 'recommendation' not in intent:
                print('the count for recommendation is', count)
                return False
            elif intent == 'recommendation' or intent == 'recommendation.attributes' or intent == 'recommendation.new':
                count +=1
                print('the count for recommendation is', count)


        # if count >=3:
        #     return True
        # else:
        #     print('the count for recommendation is',count)
        #     return False
    if too_much_recommendation(request):
        handler.transfer_request_to_dict(request.json,'')

        fulfillmentResponse = {
            'fulfillment_response': {
                'messages': [
                    # {
                    #     'text': 'It seems you have check several recommendations. Would you like to check the exhibits in this virtual museum?'},
                    {'payload':
                        {'richContent': [[{'type':'info',
                                           'title': 'Oops',
                                           'subtitle':'It seems that you have spent some time on the recommendations. Would you like to discover more exhibits in this virtual museum?'},
                            {"type": "chips",
                             "options": [{"text": 'Yes, stop the recommendation'},
                                         {"text": 'No, I want more recommendations.'}]}]]}}
                ]
            },
        }
        return jsonify(fulfillmentResponse)

    print('the tag is ',tag)
    if tag == 'recommendation' or tag == 'another':
        session = request.json['sessionInfo']['session'].split('/')[-1]

        # avoid recommending entities repetitively
        exception = handler.history[handler.history['sessionInfo.session'].isin([session])]['response.entity'].to_list() # here we record the previous recommended items
        # here we include the session intent parameters to the exception
        # for intent in handler.history[handler.history['sessionInfo.session'].isin([session])]['intentInfo.parameters.resolvedValue'].to_list():
        #     if intent != None:
        #         for i in intent:
        #             exception.append(i)
        print(exception)

        # here we record the last intent parameter as current entity, which is the entity user searched
        current_entity =  handler.history[handler.history['sessionInfo.session'].isin([session])]['intentInfo.parameters.resolvedValue'].to_list()
        print("current is ",current_entity) # !!!!this could be empty!!!! how to solve

        for i in reversed(current_entity):
            if isinstance(i,list):
                parameter = i[0].replace('\n','')
                break
        # parameters_dic = request.json['sessionInfo']['parameters']
        # key_para = list(parameters_dic.keys())[0]
        # parameter = parameters_dic[key_para]
        print("parameter is: ", parameter,'the type of parameter is {}'.format(type(parameter)))
        if request.json['text'] == "Show me similar exhibits like this exhibit." or request.json['text'] == "Another one" or \
                'exhibit' in request.json['text'] or 'painting' in request.json['text']  :
            label_preference = 'Exhibit'
        else:
            label_preference = handler.decide_label_preference('recommendation',session)
        print('prefered label is', label_preference)
        current_nodeid, suggest_nodeid = get_similarity(parameter,label=label_preference,exception_list=exception)

        # handler = ArtGraph()
        current_data = handler.search_by_nodeId(current_nodeid)
        data = handler.search_by_nodeId(suggest_nodeid)
        current_uri = current_data[0]['n']['uri']
        print("the data we got is :", data)
        name = data[0]['n']['name']
        description = data[0]['n']['description']
        uri = data[0]['n']['uri']
        query_for_graph = draw_graph(uri1=current_uri,uri2=uri).replace('RETURN p',"RETURN p as path, NODES(p) as nodes,relationships(p) as rel")
        handler.g.run(query_for_graph).data()
        # handler.
        handler.transfer_request_to_dict(request.json,parameter,name,query_for_graph)
        print("name is {}\ndesc is {}\nuri is {}\n".format(name,description,uri))
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
                                        },
                                        # {
                                        #     "type": "button",
                                        #     "icon": {
                                        #         "type": "chevron_right",
                                        #         "color": "#FF9800"
                                        #     },
                                        #     "text": "Knowledge Graph",
                                        #     "link": "", # the api address
                                        #
                                        # },
                                        {
                                            "type": "chips",
                                            "options": [
                                                {
                                                    "text": "Another one"},
                                                {"text": "Why this one?"},
                                                {"text": "Stop recommendation?"}
                                            ]
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
                                        },
                                        # {
                                        #     "type": "button",
                                        #     "icon": {
                                        #         "type": "chevron_right",
                                        #         "color": "#FF9800"
                                        #     },
                                        #     "text": "Knowledge Graph",
                                        #     "link": "", # the api address
                                        #
                                        # },
                                        {
                                            "type": "chips",
                                            "options": [
                                                {
                                                    "text": "Another one"},
                                                {"text": "Why this one?"},
                                                {"text": "Stop recommendation?"}
                                            ]
                                        }

                                    ]
                                ]
                            }

                    }
                    ]
                },
            }
            return jsonify(fulfillmentResponse)
    elif tag == 'connection':
        # for the connection, we give the connection between the suggested item and original item
        # 1. get the Cypher from the chat history
        # 2. build the reply pattern to show the connection between suggested item and original item, offer the knowledge graph
        # 3. give options to user, to let agent give another recommendation, other paintings with same objects, or stop the recommendation

        session = request.json['sessionInfo']['session'].split('/')[-1]

        Cypher = handler.history[handler.history['sessionInfo.session'].isin([session])].iloc[-1]['Cypher']
        print('the cypher for connection is ', Cypher)
        # if 'where NOT  a.name' not in Cypher:
        last_entity =  handler.history[handler.history['sessionInfo.session'].isin([session])].iloc[-1]['response.entity']
        query_data = handler.g.run(Cypher).data()
        parameter = request.json['sessionInfo']['parameters'].values()

        handler.transfer_request_to_dict(request.json,last_entity)
        print("query_data is",query_data)
        pattern_list,relationship_dic = connection_pattern(query_data)
        if query_data == [] or pattern_list == []: # there is no such graph
            print('the query data is empty')
            fulfillmentResponse = {
                'fulfillment_response': {
                    'messages': [{
                        'payload':
                            {
                                "richContent": [[{
                                        "type": "info",
                                        "title": 'Not Found',
                                        "subtitle": "Unfortunately, after searching in our knowledge graph, these two items do not share a common attributes. "

                                    },
                                {"type": "chips",
                                 "options": [{"text":'Another one'},{"text":'Stop recommendation'}]}]]}}
                    ]
                },
            }
            return jsonify(fulfillmentResponse)
        else:
            object_list = []
            for i in relationship_dic:
                object_list.extend(relationship_dic[i])
            object_list_text = []
            for obj in object_list:
                object_list_text.append( { "text":obj})
            object_list_text.append({"text": 'Another one'})
            object_list_text.append({"text":'Stop recommendation'})
            pattern_list[-1]['subtitle'] = 'Select a option below to check other paintings with the listed attribute or stop the recommendation.'

            # pattern_list.append({
            #                                 "type": "button",
            #                                 "icon": {
            #                                     "type": "chevron_right",
            #                                     "color": "#FF9800"
            #                                 },
            #                                 "text": "Click to check the Knowledge Graph",
            #                                 "link": "", # address of api
            #
            #                             })
            fulfillmentResponse = {
                'fulfillment_response': {
                    'messages': [{
                        'payload':
                            {
                                "richContent": [
                                    pattern_list,
                                    [
                                        {"type": "chips",
                                         "options": object_list_text}]

                                ]
                            }

                    }
                    ]
                },
            }
            return jsonify(fulfillmentResponse)
    elif tag == 'attribute':
        # here is to find another paintings with the same attributes
        session = request.json['sessionInfo']['session'].split('/')[-1]
        exception_list = handler.history[handler.history['sessionInfo.session'].isin([session])]['sessionInfo.parameters.value'].to_list() # here we record the previous recommended items
        response_list = handler.history[handler.history['sessionInfo.session'].isin([session])]['response.entity'].to_list() # here we record the previous recommended items
        response = []
        for i in response_list:
            if isinstance(i,str):
                response.append(i)
        exception = []
        for l in exception_list:
            if isinstance(l,list):
                exception.extend(l)
        exception = list(set(exception))+response
        if 'parameters' in list(request.json['intentInfo'].keys()):

            key = list(request.json['intentInfo']['parameters'].keys())[-1]
            parameter = request.json['intentInfo']['parameters'][key]['resolvedValue'].replace('\n','')
        else:
            parameter_list = handler.history[handler.history['sessionInfo.session'].isin([session])][
                'intentInfo.parameters.resolvedValue'].to_list()
            key_list = handler.history[handler.history['sessionInfo.session'].isin([session])][
                'intentInfo.parameters.type'].to_list()
            for i,j in zip(reversed(parameter_list),reversed(key_list)):
                print(i,j)
                if not pd.isna(i):
                    parameter = i[0].replace('\n','')
                    key = list(j)[-1]
                    break
        # query = "MATCH (a),  (a)-[]-(b{name:'"+parameter+"'}) RETURN a limit 1"
        query = "MATCH (a),  (a)-[]-(b{name:'"+parameter+"'}) where NOT  a.name  in"+str(exception)+"  RETURN a limit 1"
        data = handler.g.run(query).data()
        
        if data == []:  # there is no such graph
            handler.transfer_request_to_dict(request.json, parameter, Cypher=query)
            fulfillmentResponse = {
                'fulfillment_response': {
                    'messages': [

                        {'payload':
                            {'richContent': [[{
                                        "type": "info",
                                        "title": 'Not Found',
                                        "subtitle": "Sorry, after searching in our knowledge base, there is no pianting with this attribute. Click \"another one\" to find a new recommendation."

                                    },
                                {"type": "chips",
                                 "options": [{"text":'Another one'},{"text":'Stop recommendation'}]}]]}}
                    ]
                },
            }
            return jsonify(fulfillmentResponse)
        else:
            name = data[0]['a']['name']
            des = data[0]['a']['description']
            uri = data[0]['a']['uri']
            handler.transfer_request_to_dict(request.json,parameter,name,Cypher = query)

            try:
                img = data[0]['a']['img']
            except:
                print("no image for ",name)
                img = ''
            def attribute_to_text(key,parameter):
                if key == 'genre':
                    text = 'It also has '+parameter+' as its genre.'
                elif key == 'material':
                    text = 'It also has '+parameter+' as its material.'
                elif key == 'movement':
                    text = 'It also belongs to the movement '+parameter
                elif key == 'keyword':
                    text = 'It also depicts '+parameter
                elif key == 'collection':
                    text = 'It is also in the '+parameter
                elif key == 'exhibition':
                    text = 'It is also in the '+parameter
                elif key == 'creator' or key == 'person':
                    text = 'It is also created by '+parameter
                return text
            fulfillmentResponse = {
                'fulfillment_response': {
                    'messages': [{
                        'payload':
                            {
                                "richContent": [
                                    [{
                                        "type": "image",
                                        "rawUrl": img,
                                        "accessibilityText": name
                                    },
                                    {
                                        "type": "info",
                                        "title": name,
                                        "subtitle": des+"\n" +attribute_to_text(key,parameter),
                                        "actionLink": uri
                                    }],
                                    [
                                        {"type": "chips",
                                         "options": [{'text':'Another related entity'}, {'text':'Stop recommendation'}]}]
                                ]
                            }

                    }
                    ]
                },
            }
            return jsonify(fulfillmentResponse)
    elif tag == 'toomuch.positive':
        session = request.json['sessionInfo']['session'].split('/')[-1]
        unchecked_exhibits = handler.history[handler.history['sessionInfo.session'].isin([session])].iloc[-1][
            'exhibit_unchecked']  # here we record the previous recommended items
        handler.transfer_request_to_dict(request.json, '')
        if len(unchecked_exhibits) >=8:
            slice = random.sample(unchecked_exhibits,3)
            print(slice)
            fulfillmentResponse = {
                'fulfillment_response': {
                    'messages': [{
                        'payload':
                            {
                                "richContent": [
                                    [
                                        {"type": "chips",
                                         "options": [{'text': slice[0].split(',')[0].split(': ')[0]}, {"text":slice[1].split(',')[0].split(': ')[0]},
                                                     {'text': slice[2].split(',')[0].split(': ')[0]}]}]
                                ]
                            }

                    }
                    ]
                },
            }
            return jsonify(fulfillmentResponse)
        else:
            options = []
            if len(unchecked_exhibits) >= 3:
                slice = random.sample(unchecked_exhibits, 3)
                fulfillmentResponse = {
                    'fulfillment_response': {
                        'messages': [{
                            'payload':
                                {
                                    "richContent": [
                                        [
                                            {"type": "chips",
                                             "options": [{'text': slice[0].split(',')[0].split(': ')[0]},
                                                         {"text": slice[1].split(',')[0].split(': ')[0]},
                                                         {'text': slice[2].split(',')[0].split(': ')[0]},
                                                         {'text':'Finish the visiting'}]}]
                                    ]
                                }

                        }
                        ]
                    },
                }
                return jsonify(fulfillmentResponse)
            else:

                for i in unchecked_exhibits:
                    options.append({'text': i})
                options.append({'text':'Finish the visiting'})
                fulfillmentResponse = {
                    'fulfillment_response': {
                        'messages': [{
                            'payload':
                                {
                                    "richContent": [
                                        [
                                            {"type": "chips",
                                             "options": options}]
                                    ]
                                }

                        }
                        ]
                    },
                }
                return jsonify(fulfillmentResponse)
    elif tag == 'end':
        session = request.json['sessionInfo']['session'].split('/')[-1]
        checked_exhibits = handler.history[handler.history['sessionInfo.session'].isin([session])].iloc[-1][
            'exhibit_checked']  # here we record the previous recommended items
        parameters_types = handler.history[handler.history['sessionInfo.session'].isin([session])].iloc[-1][
            'sessionInfo.parameters.type']

        parameters_values = handler.history[handler.history['sessionInfo.session'].isin([session])].iloc[-1][
            'sessionInfo.parameters.value']


        response_entity = handler.history[handler.history['sessionInfo.session'].isin([session])][
            'response.entity'].to_list()
        paintings_list = []
        for item in response_entity:
            if isinstance(item,str):
                paintings_list.append(item)
                print(item)

        all_entity_list = checked_exhibits+paintings_list+parameters_values
        print("all_entity_list is ",all_entity_list)
        if 'Self-portrait' in all_entity_list:

            all_entity_list.remove('Self-portrait')
        new_query = '''
        MATCH (n) where n.name IN {}
        WITH collect(n) as nodes
        UNWIND nodes as n
        UNWIND nodes as m
        WITH * WHERE id(n) < id(m)
        MATCH path = allShortestPaths( (n)-[*..2]-(m) )
        RETURN path
        '''.format(str(all_entity_list))
        print('new_query is',new_query)
        query = draw_graph(new_query=new_query)
        fulfillmentResponse = {
            'fulfillment_response': {
                'messages': [{
                    'payload':
                        {
                            "richContent": [
                                [{'type':'info',
                                  'title':'Congratulation!',
                                 'subtitle':'You finished the visiting!\n\n Through this conversation, {} exhibits within this museum are checked.\n\n {} paintings in other collections are recommended to you, do you like them? \n\n And you explored {} types of relationships in my knowledge base!\n\n Hope you enjoy the chat. Have a nice day!'.format(len(checked_exhibits),len(response_entity),len(parameters_types))},

                                 # {
                                 #     "type": "button",
                                 #     "icon": {
                                 #         "type": "chevron_right",
                                 #         "color": "#FF9800"
                                 #     },
                                 #     "text": "Click to check the Knowledge Graph",
                                 #     "link": "", # the api address
                                 #
                                 # }
                                 ]
                            ]
                        }

                }
                ]
            },
        }
        history = pd.read_csv('history.csv')
        history.to_csv(r'user_evaluation\\'+session.split(':')[0]+".csv")
        return jsonify(fulfillmentResponse)


# run the app
handler = ArtGraph()
handler_es = graph_database_es.ArtGraph()
if __name__ == '__main__':
    # model = user_model()

    app.run(host='0.0.0.0', port=5000)
    # http_tunnel = ngrok.connect("localhost:5000", bind_tls=True)
    # tunnels = ngrok.get_tunnels()