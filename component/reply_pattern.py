'''
based on the information retrived from neo4j
give a dialogflow reply
input: answer from neo4j, a list
            here we assume there is only one element in the list
output: a dialogflow reply, json
'''
import random
import re
def suggest_question_pattern(label,parameter=""):

    if label == 'Collection':
        pattern ={
                                            "type": "chips",
                                            "options": [
                                                {
                                                    "text": "Which museum owns " + parameter +"?"}
                                            ]
                                        }
        return pattern
    elif label == 'Material':
        pattern = {
            "type": "chips",
            "options": [
                {
                    "text": "What is the material of " + parameter + "?"}
            ]
        }
        return pattern
    elif label == 'Genre':
        pattern = {
            "type": "chips",
            "options": [
                {
                    "text": "What is the Genre of " + parameter + "?"}
            ]
        }
        return pattern
    elif label == 'Keyword':
        pattern = {
            "type": "chips",
            "options": [
                {
                    "text": "What is the key element in " + parameter + "?"}
            ]
        }
        return pattern

    elif label == 'Movement':
        pattern = {
            "type": "chips",
            "options": [
                {
                    "text": "What movement " + parameter + " belongs to?"}
            ]
        }
        return pattern
    elif label == 'Person':
        pattern = {
            "type": "chips",
            "options": [
                {
                    "text": "Who created " + parameter + "?"}
            ]
        }
        return pattern
    elif label == 'Exhibition':
        pattern = {
            "type": "chips",
            "options": [
                {
                    "text": "Which exhibition shows " + parameter + "?"}
            ]
        }
        return pattern
    elif label == 'date':
        pattern = {
            "type": "chips",
            "options": [
                {
                    "text": "When was " + parameter + " created?"}
            ]
        }
        return pattern

def reply_pattern(answer,type='answer',parameter = "",question_types=''):
    if type=='answer':
        print('received answer in reply_pattern is',answer)
        question_type = question_types['question_types'][0]
        print("question_type is",question_type)
        if 'image' in question_type:
            for key, value in answer[0].items():
                response = {
                    'fulfillment_response': {
                        'messages': [{
                            'payload':
                                {
                                    "richContent": [
                                        [
                                            {
                                                "type": "image",
                                                "rawUrl": value,
                                                "accessibilityText": ''
                                            }
                                        ]
                                    ]
                                }

                        }
                        ]
                    },
                }
                return response
        elif 'date' in question_type:
            for key, value in answer[0].items():
                response = {'fulfillment_response':
                    {'messages': [
                        {'payload':
                            {
                                "richContent": [
                                    [

                                        {
                                            "type": "info",
                                            "title": 'It was in ' + str(value)[0:4]
                                        }

                                    ]
                                ]
                            }}
                    ]}
                }
                return response
        elif 'description' in question_type:
            for key, value in answer[0].items():
                response = {'fulfillment_response':
                    {'messages': [
                        {'payload':
                            {
                                "richContent": [
                                    [

                                        {
                                            "type": "info",
                                            "title": str(value)
                                        }

                                    ]
                                ]
                            }}
                    ]}
                }
                return response
        else:
            template_response = {'fulfillment_response':
                    {'messages': [
                        {'payload':
                            {
                                "richContent": [
                                    [



                                    ]
                                ]
                            }}
                    ]}
                }
            for dic in answer:
                key_node = list(dic.keys())[0]
                img = ''
                try:
                    img = dic[key_node]['img']
                except:
                    img = ''
                if img == '':

                    response_part= {
                                                 "type": "info",
                                                "title": dic[key_node]['name'],
                                                "subtitle": dic[key_node]['description'],
                                                "actionLink": dic[key_node]['uri']
                                            }
                    template_response['fulfillment_response']['messages'][0]['payload']['richContent'][0].append(
                        response_part)
                else:
                    img_part = {
                        "type": "image",
                        "rawUrl": img,
                        "accessibilityText": dic[key_node]['name']
                    }
                    response_part = {
                        "type": "info",
                        "title": dic[key_node]['name'],
                        "subtitle": dic[key_node]['description'],
                        "actionLink": dic[key_node]['uri']
                    }

                    template_response['fulfillment_response']['messages'][0]['payload']['richContent'][0].append(
                        img_part)

                    template_response['fulfillment_response']['messages'][0]['payload']['richContent'][0].append(response_part)
            return template_response
        # here we assume there is only one element in the list
        for key, value in answer[0].items():
            if value == 'None':
                response = {'fulfillment_response':
                    {'messages': [
                        {'text':
                            {
                                "text": [
                                    ['Sorry, we do not have it in the knowledge base! Try another question if you wish.'

                                    ]
                                ]
                            }}
                    ]}
                }
                return response
            if 'name' in key or 'uri' in key:
                response = {'fulfillment_response':
                                {'messages': [
                                    {'payload':
                            {
                                "richContent": [
                                    [

                                        {
                                            "type": "info",
                                            "title": value
                                        },
                                        {
                                            "type": "chips",
                                            "options": [
                                                {
                                                    "text": "Show me similar item like " + value
                                                }
                                            ]
                                        }

                                    ]
                                ]
                            }}
                                ]}
                            }
                return response

            elif 'date' in key:
                response = {'fulfillment_response':
                                {'messages': [
                                    {'payload':
                            {
                                "richContent": [
                                    [

                                        {
                                            "type": "info",
                                            "title": 'The time is '+str(value)[0:4]
                                        }

                                    ]
                                ]
                            }}
                                ]}
                            }
                return response
    elif type == 'suggest_question':
        print("entity list received for suggesting question is :", answer)
        target = random.randint(0, len(answer)-1)
        label = answer[target]['node'].labels
        if str(label).count(':') >1: # deal with multiple label

            label = ':'+random.choice(re.findall(r":([^\s:]+)",str(label)))

        target2 = random.randint(0, len(answer)-1)
        if target2 > len(answer) / 2 or target2 == target:
            label2 = 'date'
        else:
            label2 = answer[target2]['node'].labels
            label2 = ':' + random.choice(re.findall(r":([^\s:]+)", str(label2)))
            if label2 == label:
                label2 = 'date'
        print('we got label {}, label2 {} and parameter {}'.format(label,label2,parameter))
        pattern1 = suggest_question_pattern(str(label).replace(':','') ,parameter=parameter)
        pattern2 = suggest_question_pattern(str(label2).replace(':',''), parameter=parameter)
        if not pattern1:
            print('pattern1 error', target,"\nLabel is", label)
        elif not pattern2:
            print('pattern2 error', target2, "\nLabel is",label2)

        response = {'fulfillment_response':
            {'messages': [
                {'payload':
                    {
                        "richContent": [
                            [

                                pattern1,
                                pattern2

                            ]
                        ]
                    }}
            ]}
        }
        return response

pattern = suggest_question_pattern('Movement' ,parameter='Two moors')
print(pattern)
