from py2neo import Node, Relationship, Graph
from component.question_classfier import *
from component.question_parser import *
import random
import pandas as pd
class ArtGraph:
    def __init__(self):
        # self.g = Graph(
        #     scheme="neo4j",
        #     host="localhost",
        #     port=7687,
        #     auth=("neo4j", "000000"))
        self.g = Graph("neo4j+ssc://bda6cbfc.databases.neo4j.io", auth=("neo4j", "1nNlEWXcOmHfyRAJupBjyhoc5aGAJu-OOP2YqcWh62o"))
        # self.g = GraphDatabase.driver("neo4j+s://bda6cbfc.databases.neo4j.io", auth=("neo4j", "1nNlEWXcOmHfyRAJupBjyhoc5aGAJu-OOP2YqcWh62o"))
        self.node_name_list = ['Paintings','Keyword','Country','Genre','Material','Collection','Person','Exhibition','Movement','City']
        self.Paintings = []
        self.Keyword = []
        self.Country = []
        self.Genre = []
        self.Material = []
        self.Collection = []
        self.Person = []
        self.Exhibition = []
        self.Movement  = []
        self.City = []
        self.num_limit = 20
        self.classifier = QuestionClassifier()
        self.parser = QuestionPaser()
        with open('dict/Paintings.txt', encoding="utf-8") as f:
            self.Paintings = [i.strip() for i in f.readlines()]

        with open('dict/Keyword.txt', encoding="utf-8") as f:
            self.Keyword = [i.strip() for i in f.readlines()]

        with open('dict/Country.txt', encoding="utf-8") as f:
            self.Country = [i.strip() for i in f.readlines()]

        with open('dict/Genre.txt', encoding="utf-8") as f:
            self.Genre = [i.strip() for i in f.readlines()]

        with open('dict/Material.txt', encoding="utf-8") as f:
            self.Material = [i.strip() for i in f.readlines()]

        with open('dict/Collection.txt', encoding="utf-8") as f:
            self.Collection = [i.strip() for i in f.readlines()]



        with open('dict/Person.txt', encoding="utf-8") as f:
            self.Person = [i.strip() for i in f.readlines()]

        with open('dict/Exhibition.txt', encoding="utf-8") as f:
            self.Exhibition = [i.strip() for i in f.readlines()]

        with open('dict/Movement.txt', encoding="utf-8") as f:
            self.Movement = [i.strip() for i in f.readlines()]

        with open('dict/City.txt', encoding="utf-8") as f:
            self.City = [i.strip() for i in f.readlines()]
        # print(self.Paintings)

        self.exhibit_checked = []
        self.exhibit_unchecked = ['Two moors', 'King Caspar', 'Don Miguel de Castro, Emissary of Congo',
                                  'Diego Bemba, a Servant of Don Miguel de Castro',
                                  'Pedro Sunda, a Servant of Don Miguel de Castro',
                                  'Map of Paranambucae', 'Portrait of a Black Girl', 'Portrait of a Man',
                                  'Man in a Turban',
                                  'Head of a Boy in a Turban', 'Doritos',
                                  'The New Utopia Begins Here: Hermina Huiswoud',
                                  'The Unspoken Truth', 'Ilona', 'Head of a Boy', 'The Market in Dam Square']

        self.preference = {'Paintings': 1,
                           'Person': 1,
                           'Collection': 1,
                           'Exhibition': 1,
                           'Genre': 1,
                           'Keyword': 1,
                           'Movement': 1,
                           'Material': 1,
                           'Exhibit': len(self.exhibit_unchecked)}

        self.history = pd.DataFrame(columns = [ 'intentInfo.displayName',
                                    'intentInfo.confidence',
                                    'intentInfo.parameters.type',
                                    'intentInfo.parameters.originalValue',
                                    'intentInfo.parameters.resolvedValue',
                                    'sessionInfo.session',
                                    'sessionInfo.parameters.type',
                                    'sessionInfo.parameters.value',
                                    'fulfillmentInfo.tag', 'text',
                                    'response.entity','exhibit_checked','exhibit_unchecked','preference','Cypher'])

        self.preference_list = ['Paintings','Keyword','Genre','Material','Collection','Person','Exhibition','Movement']

    def build_nodes(self):
        # kinds of nodes
        Paintings = []
        Keyword = []
        Country = []
        Genre = []
        Material = []
        Collection = []
        Person = []
        Exhibition = []
        Movement = []
        City = []
        nodes_list=[Paintings,Keyword,Country,Genre,Material,Collection,Person,Exhibition,Movement,City]
        # kinds of relations
        in_collection = [] #collection-[]-paintings
        keyword = [] # paintings-[]-depicts
        has_genre = [] # paintings - [] - genre
        has_material = [] # paintings - [] - material
        country = [] # paintings - [] - country

        for index,nodes in enumerate(self.node_name_list):
            print(nodes)
            sparql_for_name = "MATCH (n:"+str(nodes)+") RETURN n"
            nodes_data_all = self.g.run(str(sparql_for_name)).data()
            for node in nodes_data_all:
                try:
                    nodes_list[index].append(node['n']['name'])

                except :
                    pass

            # if nodes == 'Paintings':
            #     with open('./dict/' + str('title') + '.txt', 'w+', encoding="utf-8") as f:
            #         f.write('\n'.join(list(title)))
        # write the txt of data
            with open('./dict/'+str(nodes)+'.txt', 'w+',encoding="utf-8") as f:
                f.write('\n'.join(list(nodes_list[index])))


    def show_exhibit(self,exhibit_in_dialog):
        if exhibit_in_dialog in self.Paintings:
            sparql_for_name = "MATCH (n:Paintings) WHERE n.name = '" + str(exhibit_in_dialog) +"' RETURN n"
            data = self.g.run(str(sparql_for_name)).data()
            print(data)
            return data
        # elif exhibit_in_dialog in self.Paintings_title:
        #     sparql_for_name = "MATCH (n:Paintings) WHERE n.title = '" + str(exhibit_in_dialog) + "' RETURN n"
        #     data = self.g.run(str(sparql_for_name)).data()
        #     print(data)
        #     return data
        elif exhibit_in_dialog in self.Person:
            sparql_for_name = "MATCH (n:Person) WHERE n.name = '" + str(exhibit_in_dialog) + "' RETURN n"
            data = self.g.run(str(sparql_for_name)).data()
            print(data)
            return data
        else:
            return None

    def search_by_nodeId(self, nodeid):
        sparql_with_nodeid = "MATCH (n) WHERE id(n) = "+str(nodeid)+" RETURN n"
        data = self.g.run(str(sparql_with_nodeid)).data()
        print(data)
        return data

    # def update_exhibit(self,exhibit_name):
    #     if exhibit_name in self.exhibit_unchecked:
    #         self.exhibit_unchecked.remove(exhibit_name)
    #         self.exhibit_checked.append(exhibit_name)
    #         self.preference['Exhibit'] = len(self.exhibit_unchecked)

    # def update_user_preference(self,item):
    # 
    #     if item in self.Paintings and self.preference['Paintings'] <=10:
    #         self.preference['Paintings'] +=1
    #     if item in self.Collection and self.preference['Collection'] <=10:
    #         self.preference['Collection'] +=1
    #     if item in self.Exhibition and self.preference['Exhibition'] <=10:
    #         self.preference['Exhibition'] +=1
    #     if item in self.Genre and self.preference['Genre'] <=10:
    #         self.preference['Genre'] +=1
    #     if item in self.Keyword and self.preference['Keyword'] <=10:
    #         self.preference['Keyword'] +=1
    #     if item in self.Movement and self.preference['Movement'] <=10:
    #         self.preference['Movement'] +=1
    #     if item in self.Material and self.preference['Mterial'] <=10:
    #         self.preference['Mterial'] +=1
    #     if item in self.Person and self.preference['Person'] <=10:
    #         self.preference['Person'] +=1


    def transfer_request_to_dict(self,request_json, item_preference, returned_entity= [],Cypher = None ):
        '''
        here to store the interaction between dialogflow and end user, we save part of the information in requests from dialogflow
        and the returned entity from webhook to the dialogflow as a dataframe and update these information, as well as user's
        preference.
        :param request_json: the request sent from dialogflow, json
        :param returned_entity: the name of returned entity from webhook service, string
        :param item_preference: the item user checked that should have impact preference, string
        :return:
        '''
        print("=" * 10 + 'item_preference and returned_entity' + "=" * 10)
        print("item_preference is {}, returned_entity is {}".format(item_preference, returned_entity))
        d = {}

        if "intentInfo" in request_json.keys():
            if 'displayName' in request_json['intentInfo'].keys():
                d["intentInfo.displayName"] = request_json["intentInfo"]['displayName']
                d["intentInfo.confidence"] = request_json["intentInfo"]['confidence']
            if 'parameters' in request_json['intentInfo'].keys():
                d["intentInfo.parameters.type"] = request_json["intentInfo"]['parameters'].keys()
                d['intentInfo.parameters.originalValue'] = [request_json["intentInfo"]['parameters'][i]["originalValue"]
                                                            for i in request_json["intentInfo"]['parameters'].keys()]
                d['intentInfo.parameters.resolvedValue'] = [request_json["intentInfo"]['parameters'][i]["resolvedValue"]
                                                            for i in request_json["intentInfo"]['parameters'].keys()]
        if "sessionInfo" in request_json.keys():
            if 'session' in request_json['sessionInfo'].keys():
                d['sessionInfo.session'] = request_json['sessionInfo']['session'].split('/')[-1]  # get the session id
            if 'parameters' in request_json['sessionInfo'].keys():
                d['sessionInfo.parameters.type'] = request_json['sessionInfo']['parameters'].keys()
                d['sessionInfo.parameters.value'] = [request_json["sessionInfo"]['parameters'][i].replace('\n','') for
                                                     i in request_json["sessionInfo"]['parameters'].keys()]
        if 'fulfillmentInfo' in request_json.keys():
            if 'tag' in request_json['fulfillmentInfo'].keys():
                d["fulfillmentInfo.tag"] = request_json["fulfillmentInfo"]['tag']
        if 'text' in request_json.keys():
            d['text'] = request_json['text']
        d['response.entity'] = returned_entity


        if Cypher:
            d['Cypher'] = Cypher
        else:
            d['Cypher'] = ''
        # here check if this session exists in history
        if d['sessionInfo.session'] in self.history['sessionInfo.session'].to_list():
            d['exhibit_checked'] = self.history[self.history['sessionInfo.session'].isin([d['sessionInfo.session']])].iloc[-1]['exhibit_checked']
            d['exhibit_unchecked'] = self.history[self.history['sessionInfo.session'].isin([d['sessionInfo.session']])].iloc[-1]['exhibit_unchecked']
            d['preference'] = self.history[self.history['sessionInfo.session'].isin([d['sessionInfo.session']])].iloc[-1]['preference']
        else:
            d['exhibit_checked'] = []
            d['exhibit_unchecked'] = ['Two moors', 'King Caspar', 'Don Miguel de Castro, Emissary of Congo',
                                  'Diego Bemba, a Servant of Don Miguel de Castro',
                                  'Pedro Sunda, a Servant of Don Miguel de Castro',
                                  'Map of Paranambucae', 'Portrait of a Black Girl', 'Portrait of a Man',
                                  'Man in a Turban',
                                  'Head of a Boy in a Turban', 'Doritos',
                                  'The New Utopia Begins Here: Hermina Huiswoud',
                                  'The Unspoken Truth', 'Ilona', 'Head of a Boy', 'The Market in Dam Square']
            d['preference'] = {'Paintings': 1,
                           'Person': 1,
                           'Collection': 1,
                           'Exhibition': 1,
                           'Genre': 1,
                           'Keyword': 1,
                           'Movement': 1,
                           'Material': 1,
                           'Exhibit': len(d['exhibit_unchecked'])}
        # update the checked list and preference
        if (isinstance(item_preference,list)):
            for item in item_preference:
                if item in d['exhibit_unchecked']:
                    d['exhibit_unchecked'].remove(item)
                    d['exhibit_checked'].append(item)
                    d['preference']['Exhibit'] = len(d['exhibit_unchecked'])

                if item in self.Paintings and d['preference']['Paintings'] <= 10:
                    d['preference']['Paintings'] += 1
                if item in self.Collection and d['preference']['Collection'] <= 10:
                    d['preference']['Collection'] += 1
                if item in self.Exhibition and d['preference']['Exhibition'] <= 10:
                    d['preference']['Exhibition'] += 1
                if item in self.Genre and d['preference']['Genre'] <= 10:
                    d['preference']['Genre'] += 1
                if item in self.Keyword and d['preference']['Keyword'] <= 10:
                    d['preference']['Keyword'] += 1
                if item in self.Movement and d['preference']['Movement'] <= 10:
                    d['preference']['Movement'] += 1
                if item in self.Material and d['preference']['Mterial'] <= 10:
                    d['preference']['Mterial'] += 1
                if item in self.Person and d['preference']['Person'] <= 10:
                    d['preference']['Person'] += 1
        elif (isinstance(item_preference,str)):

            if item_preference in d['exhibit_unchecked']:
                d['exhibit_unchecked'].remove(item_preference)
                d['exhibit_checked'].append(item_preference)
                d['preference']['Exhibit'] = len(d['exhibit_unchecked'])

            if item_preference in self.Paintings and d['preference']['Paintings'] <=10:
                d['preference']['Paintings'] +=1
            if item_preference in self.Collection and d['preference']['Collection'] <=10:
                d['preference']['Collection'] +=1
            if item_preference in self.Exhibition and d['preference']['Exhibition'] <=10:
                d['preference']['Exhibition'] +=1
            if item_preference in self.Genre and d['preference']['Genre'] <=10:
                d['preference']['Genre'] +=1
            if item_preference in self.Keyword and d['preference']['Keyword'] <=10:
                d['preference']['Keyword'] +=1
            if item_preference in self.Movement and d['preference']['Movement'] <=10:
                d['preference']['Movement'] +=1
            if item_preference in self.Material and d['preference']['Material'] <=10:
                d['preference']['Material'] +=1
            if item_preference in self.Person and d['preference']['Person'] <=10:
                d['preference']['Person'] +=1

        if isinstance(returned_entity, list):
            for item in returned_entity:
                if item in d['exhibit_unchecked']:
                    d['exhibit_unchecked'].remove(item)
                    d['exhibit_checked'].append(item)
                    d['preference']['Exhibit'] = len(d['exhibit_unchecked'])
        elif isinstance(returned_entity, str):
            if returned_entity in d['exhibit_unchecked']:
                d['exhibit_unchecked'].remove(returned_entity)
                d['exhibit_checked'].append(returned_entity)
                d['preference']['Exhibit'] = len(d['exhibit_unchecked'])
        self.history = self.history.append(d,ignore_index=True)
        print("=" * 10+'history'+"=" * 10)
        print(d)
        print(self.history)
        print("=" * 20)
        self.history.to_csv("history.csv")

    def decide_label_preference(self,mode,session):
        '''
        :mode: suggest the mode
        based on the user_peference to choose a label to suggest, in suggest_question mode,
        the question should be based on the current item.
        :return: return the label choose randomly
        '''
        if session in self.history['sessionInfo.session'].to_list():
            preference = self.history[self.history['sessionInfo.session'].isin([session])].iloc[-1]['preference']
        else:
            print("check decide_label_preference")
        if mode =='recommendation':
            target = random.randint(0,sum(preference.values()))
            sum_ = 0
            for k, v in preference.items():
                sum_ += v
                if sum_ >= target:
                    return k
        elif mode == 'suggest_question':
            target = random.randint(0, sum(preference.values())-preference['Exhibit'])
            sum_ = 0
            for k, v in preference.items():
                if k == 'Exhibit':
                    pass
                else:
                    sum_ += v
                    if sum_ >= target:
                        return k

    def answer_prettify(self, question):

        try:

            sqls = self.parser.parser_main(question)
            if not sqls:
                return None
            else:

                answer_neo4j = self.g.run(str(sqls[0]['sql'][0])).data()
                return answer_neo4j
        except:
            return None
        '''
        can not find anything related
        Return None and then either the ask for clarification or say sorry to the user
        '''

    def get_neighbors(self,name,type='',hop=1):
        '''
        Get the neighbor nodes of given node
        :param name: the name of the given node
        :param type: the entity type of the given node, could be ignored
        :param hop: the distance, default = 1
        :return: list of nodes
        '''
        if type != '':
            type = ':'+type
        cypher_neighbors = "MATCH (p"+type+ "{name: \""+name+"\"}) CALL apoc.neighbors.athop(p, \"belongsto_GENRE|has_CREATOR|belongsto_MOVEMENT|has_KEYWORD|on_MATERIAL|in_COLLECTION|in_EXHIBITION\", +"+str(hop)+") YIELD node RETURN node"
        data = self.g.run(str(cypher_neighbors)).data()
        return data

    def get_properties(self,name,type=""):
        '''

        :param name:
        :param type:
        :return: a list of properties's name
        '''
        if type != '':
            type = ':'+type
        cypher_properties = "Match (p"+type+"{name:\'"+name+"\'}) return keys(p)"
        data = self.g.run(str(cypher_properties)).data()
        return data


    # def get_neighbors(self,name):


if __name__ == '__main__':
    handler = ArtGraph()
    # handler.build_nodes()
    # handler.create_graphrels()
    # handler.export_data()
    data = handler.show_exhibit('Rembrandt')
    print(data)
    print('Done')
    data1 = handler.g.run("MATCH (a),  (a)-[]-(b{name:'portrait'}) RETURN a limit 1").data()
    print(data1[0]['a'])
# graph.schema.node_labels

# graph.schema.relationship_types
