'''
based on the information retrived from neo4j
give a dialogflow reply
input: answer from neo4j, a list
            here we assume there is only one element in the list
output: a dialogflow reply, json
'''
def reply_pattern(answer):
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
        elif 'img' in key:
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
