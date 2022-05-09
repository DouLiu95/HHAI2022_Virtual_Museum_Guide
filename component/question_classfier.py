import os
import ahocorasick
import string
import re
class QuestionClassifier:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        #　path for the keywords
        self.collection_path = os.path.join(cur_dir, 'dict/Collection.txt')
        self.country_path = os.path.join(cur_dir, 'dict/Country.txt')
        self.depicts_path = os.path.join(cur_dir, 'dict/Keyword.txt')
        self.genre_path = os.path.join(cur_dir, 'dict/Genre.txt')
        self.material_path = os.path.join(cur_dir, 'dict/Material.txt')
        self.paintings_path = os.path.join(cur_dir, 'dict/Paintings.txt')
        self.creator_path = os.path.join(cur_dir, 'dict/Person.txt')
        self.movement_path = os.path.join(cur_dir,'dict/Movement.txt')
        self.exhibition_path = os.path.join(cur_dir,'dict/Exhibition.txt')

        # load the keywords
        self.collection_wds = [i.strip() for i in open(self.collection_path, encoding='utf-8') if i.strip()]
        self.country_wds = [i.strip() for i in open(self.country_path, encoding='utf-8') if i.strip()]
        self.depicts_wds = [i.strip() for i in open(self.depicts_path, encoding='utf-8') if i.strip()]
        self.genre_wds = [i.strip() for i in open(self.genre_path, encoding='utf-8') if i.strip()]
        self.material_wds = [i.strip() for i in open(self.material_path, encoding='utf-8') if i.strip()]
        self.paintings_wds = [i.strip() for i in open(self.paintings_path, encoding='utf-8') if i.strip()]
        self.creator_wds = [i.strip() for i in open(self.creator_path, encoding='utf-8') if i.strip()]
        self.movement_wds = [i.strip() for i in open(self.movement_path, encoding='utf-8') if i.strip()]
        self.exhibition_wds = [i.strip() for i in open(self.exhibition_path, encoding='utf-8') if i.strip()]

        self.region_words = set(self.collection_wds + self.country_wds
                                + self.depicts_wds + self.genre_wds +
                                self.material_wds + self.paintings_wds+self.creator_wds+self.movement_wds+self.exhibition_wds )

        # build region actree
        self.region_tree = self.build_actree(list(self.region_words))
        # build dictionary
        self.wdtype_dict = self.build_wdtype_dict()

        # question keywords
        self.date_qwds = ['when','When','what time','What time','which time','time','date']
        self.image_qwds = ['image','picture','figure']
        self.material_qwds = ['material','textile']
        self.depicts_qwds = ['point','depict','element','object','component','keyword','key']
        self.genre_qwds = ['genre','style','form','category','kind','fashion']
        self.country_qwds = ['countries','country','which country','Which country','where','Where']
        self.collection_qwds = ['collection','gallery','museum']
        self.exhibition_qwds = ['exhibition']
        self.movement_qwds = ['movement']
        self.paintings_qwds = ['painting','draw','drawing','paint','artwork','work','paintings']
        self.description_qwds = ['describe','description','website','web','web page','webpage','page', 'tell me']
        self.creator_qwds = ['creator','who','Who']
        self.coordinate_qwds = ['coordinate','map','specific location','location','located']
        self.size_qwds = ['size','how much','How many','How much','how many']
        self.visitor_qwds = ['visitor','guest','tourist','sightseer']
        print('model init finished ......')

        return

    # build actree
    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    #build word type dictionary
    def build_wdtype_dict(self):
        wd_dict = dict()
        for wd in self.region_words:
            wd_dict[wd] = []
            if wd in self.collection_wds:
                wd_dict[wd].append('collection')
            if wd in self.country_wds:
                wd_dict[wd].append('country')
            if wd in self.depicts_wds:
                wd_dict[wd].append('depicts')
            if wd in self.genre_wds:
                wd_dict[wd].append('genre')
            if wd in self.material_wds:
                wd_dict[wd].append('material')
            if wd in self.paintings_wds:
                wd_dict[wd].append('paintings')
            if wd in self.creator_wds:
                wd_dict[wd].append('creator')
            if wd in self.movement_wds:
                wd_dict[wd].append('movement')
            if wd in self.exhibition_wds:
                wd_dict[wd].append('exhibition')
        return wd_dict

    '''filter the question'''

    def check_keywords(self, question):
        region_wds = []
        for i in self.region_tree.iter(question):
            wd = i[1][1]
            region_wds.append(wd)
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)
        final_wds = [i for i in region_wds if i not in stop_wds]
        for item in final_wds:
            if re.search(r"\b{}\b".format(item), question):
                pass
            else:
                final_wds.remove(item)
        print(final_wds)
        final_dict = {i: self.wdtype_dict.get(i) for i in final_wds}


        print(final_dict)
        return final_dict

    '''classify based on the question words'''

    def check_words(self, wds, sent):
        clean_words = ''.join(' ' if c in string.punctuation else c for c in sent)


        sent_token = clean_words.split()

        for wd in wds:
            if wd in sent_token:
                return True
        return False

    '''main function'''
    def classify(self, question):
        data = {}
        art_dict = self.check_keywords(question)

        if not art_dict:
            return {}
        data['args'] = art_dict
        #collect the entity label in the question
        types = []
        for type_ in art_dict.values():
            types += type_
        question_type = 'others'
        print("types from classify are:", types)
        question_types = []
        for key_ in art_dict.keys():
            if key_.startswith('Q'):
                new_key = r"http://www.wikidata.org/entity/" + key_
                art_dict[new_key] = art_dict.pop(key_)



        '''painting's basic information'''

        # e.g. which collection is the painting in?
        if self.check_words(self.collection_qwds, question) and ('paintings' in types):
            question_type = 'paintings_collection'
            question_types.append(question_type)
        # e.g. who is the creator of the painting?
        if self.check_words(self.creator_qwds, question) and ('paintings' in types):
            question_type = 'paintings_creator'
            question_types.append(question_type)
        # e.g. what is the material of the painting?
        if self.check_words(self.material_qwds, question) and ('paintings' in types):
            question_type = 'paintings_material'
            question_types.append(question_type)
        # e.g. what is the genre of the painting?
        if self.check_words(self.genre_qwds, question) and ('paintings' in types):
            question_type = 'paintings_genre'
            question_types.append(question_type)
        # e.g. which exhibition is this painting in?
        if self.check_words(self.exhibition_qwds, question) and ('paintings' in types):
            question_type = 'paintings_exhibition'
            question_types.append(question_type)
        # e.g. what movement is the painting belongs to
        if self.check_words(self.movement_qwds, question) and ('paintings' in types):
            question_type = 'paintings_movement'
            question_types.append(question_type)

        # what is the element in this painting?
        if self.check_words(self.depicts_qwds, question) and ('paintings' in types):
            question_type = 'paintings_depicts'
            question_types.append(question_type)
        # when is this painting created?
        if self.check_words(self.date_qwds, question) and ('paintings' in types):
            question_type = 'paintings_date'
            question_types.append(question_type)
        # e.g. show me the image of the paintings
        if self.check_words(self.image_qwds, question) and ('paintings' in types):
            question_type = 'paintings_image'
            question_types.append(question_type)
        # e.g. give me some more description about this
        if self.check_words(self.description_qwds, question) and ('paintings' in types):
            question_type = 'paintings_description'
            question_types.append(question_type)
        # e.g. where is this painting preserved?
        if self.check_words(self.country_qwds, question) and ('paintings' in types):
            question_type = 'paintings_country'
            question_types.append(question_type)
        # e.g. which country is this collection located?
        if self.check_words(self.country_qwds, question) and ('collection' in types):
            question_type = 'collection_country'
            question_types.append(question_type)
        # e.g. show me the museum on the map
        if self.check_words(self.coordinate_qwds, question) and ('collection' in types):
            question_type = 'collection_coordinate'
            question_types.append(question_type)
        # e.g. what else artworks are in the museum?
        if self.check_words(self.paintings_qwds, question) and ('collection' in types):
            question_type = 'collection_paintings'
            question_types.append(question_type)
        # e.g. how many collections does this museum have?
        if self.check_words(self.size_qwds, question) and ('collection' in types):
            question_type = 'collection_size'
            question_types.append(question_type)
        # give me the image of the museum
        if self.check_words(self.image_qwds, question) and ('collection' in types):
            question_type = 'collection_image'
            question_types.append(question_type)
        # when is this museum built?
        if self.check_words(self.date_qwds, question) and ('collection' in types):
            question_type = 'collection_date'
            question_types.append(question_type)
        # e.g. how many visitor in the museum
        if self.check_words(self.visitor_qwds,question) and ('collection' in types):
            question_type = 'collection_visitor'
            question_types.append(question_type)
        # e.g. give me the website of the museum
        if self.check_words(self.description_qwds, question) and ('collection' in types):
            question_type = 'collection_description'
            question_types.append(question_type)
        #e.g. show me other paintings in this genre
        if self.check_words(self.paintings_qwds, question) and ('genre' in types):
            question_type = 'genre_paintings'
            question_types.append(question_type)
        # e.g. show me other paintings with same element
        if self.check_words(self.paintings_qwds, question) and ('depicts' in types):
            question_type = 'depicts_paintings'
            question_types.append(question_type)
        # no extra information, return the description
        if (question_types == [] and 'paintings' in types) or (self.check_words(self.description_qwds, question) and ('paintings' in types)):
            question_types = ['paintings_description']

        if (question_types == [] and 'collection' in types) or (self.check_words(self.description_qwds, question) and ('collection' in types)):
            question_types = ['collection_description']

        if (question_types == [] and 'creator' in types) or (self.check_words(self.description_qwds, question) and ('creator' in types)):
            question_types = ['creator_description']

        # 将多个分类结果进行合并处理，组装成一个字典
        data['question_types'] = question_types

        return data
        # to do:
        #       how to ask about the movement?
        #       like:
        # if self.check_words(self.movement_qwds, question) and ('paintings' in types):
        #     question_type = 'paintings_movement'
        #     question_types.append(question_type)
        # e.g. where is
if __name__ == '__main__':
    handler = QuestionClassifier()
    while 1:
        question = input('input an question:')
        data = handler.classify(question)
        print(data)