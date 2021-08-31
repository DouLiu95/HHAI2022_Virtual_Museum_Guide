class QuestionPaser:

    '''build entity dict '''
    def build_entitydict(self, args):
        entity_dict = {}
        for arg, types in args.items():
            for type in types:
                if type not in entity_dict:
                    entity_dict[type] = [arg]
                else:
                    entity_dict[type].append(arg)
        # return like {'paintings':['name of the painting'],and more ...}
        return entity_dict

    '''main function'''

    def parser_main(self, res_classify):
        args = res_classify['args']
        entity_dict = self.build_entitydict(args)
        question_types = res_classify['question_types']
        sqls = []
        for question_type in question_types:
            sql_ = {}
            sql_['question_type'] = question_type
            sql = []
            if question_type == 'paintings_collection':
                sql = self.sql_transfer(question_type, entity_dict.get('paintings'))

            elif question_type == 'paintings_creator':
                sql = self.sql_transfer(question_type, entity_dict.get('paintings'))

            elif question_type == 'paintings_material':
                sql = self.sql_transfer(question_type, entity_dict.get('paintings'))
            elif question_type == 'paintings_genre':
                sql = self.sql_transfer(question_type, entity_dict.get('paintings'))
            elif question_type == 'paintings_depicts':
                sql = self.sql_transfer(question_type, entity_dict.get('paintings'))
            elif question_type == 'paintings_date':
                sql = self.sql_transfer(question_type, entity_dict.get('paintings'))
            elif question_type == 'paintings_image':
                sql = self.sql_transfer(question_type, entity_dict.get('paintings'))
            elif question_type == 'paintings_description':
                sql = self.sql_transfer(question_type, entity_dict.get('paintings'))

            elif question_type == 'paintings_country':
                sql = self.sql_transfer(question_type, entity_dict.get('paintings'))
            elif question_type == 'collection_coordinate':
                sql = self.sql_transfer(question_type, entity_dict.get('collection'))
            elif question_type == 'collection_paintings':
                sql = self.sql_transfer(question_type, entity_dict.get('collection'))
            elif question_type == 'collection_size':
                sql = self.sql_transfer(question_type, entity_dict.get('collection'))
            elif question_type == 'collection_image':
                sql = self.sql_transfer(question_type, entity_dict.get('collection'))
            elif question_type == 'collection_date':
                sql = self.sql_transfer(question_type, entity_dict.get('collection'))
            elif question_type == 'collection_visitor':
                sql = self.sql_transfer(question_type, entity_dict.get('collection'))
            elif question_type == 'collection_description':
                sql = self.sql_transfer(question_type, entity_dict.get('collection'))
            elif question_type == 'genre_paintings':
                sql = self.sql_transfer(question_type, entity_dict.get('genre'))
            elif question_type == 'depicts_paintings':
                sql = self.sql_transfer(question_type, entity_dict.get('depicts'))

            elif question_type == 'creator_description':
                sql = self.sql_transfer(question_type, entity_dict.get('creator'))

            if sql:
                sql_['sql'] = sql

                sqls.append(sql_)

        return sqls
    
    def sql_transfer(self, question_type, entities):
        # return none if no entity
        if not entities:
            return []
        # sparql query
        sql = []

        if question_type == 'paintings_collection':
            sql = ["MATCH (p:Paintings)-[r:in_COLLECTION]->(c:Collection) where p.name ='{0}' RETURN c.name ".format(i)
                   for i in entities]

        elif question_type == 'paintings_creator':
            sql = ["MATCH (p:Paintings)-[r:has_CREATOR]->(c:Person) where p.name ='{0}' RETURN c.name ".format(i)
                   for i in entities]

        elif question_type == 'paintings_material':
            sql = ["MATCH (p:Paintings)-[r:has_MATERIAL]->(c:Material) where p.name ='{0}' RETURN c.name ".format(i)
                   for i in entities]

        elif question_type == 'paintings_genre':
            sql = ["MATCH (p:Paintings)-[r:has_GENRE]->(c:Genre) where p.name ='{0}' RETURN c.name ".format(i)
                   for i in entities]

        elif question_type == 'paintings_depicts':
            sql = ["MATCH (p:Paintings)-[r:has_KEYWORD]->(c:Depicts) where p.name ='{0}' RETURN c.name ".format(i)
                   for i in entities]

        elif question_type == 'paintings_date':
            sql = ["MATCH (p:Paintings) where p.name ='{0}' RETURN p.date ".format(i)
                   for i in entities]

        elif question_type == 'paintings_image':
            sql = ["MATCH (p:Paintings) where p.name ='{0}' RETURN p.img ".format(i)
                   for i in entities]

        elif question_type == 'paintings_description':
            sql = ["MATCH (p:Paintings) where p.name ='{0}' RETURN p.uri ".format(i)
                   for i in entities]

        elif question_type == 'paintings_country':
            sql = ["MATCH (p:Paintings)-[r:in_COUNTRY]->(c:Country) where p.name ='{0}' RETURN c.name ".format(i)
                   for i in entities]

        elif question_type == 'collection_country':
            sql = ["MATCH (p:Collection)-[r:in_COUNTRY]->(c:Country) where p.name ='{0}' RETURN c.name ".format(i)
                   for i in entities]

        # elif question_type == 'collection_coordinate':
        #     sql = ["MATCH (p:Collection) where p.name ='{0}' RETURN p.coordinate ".format(i)
        #            for i in entities]

        elif question_type == 'collection_paintings':
            sql = ["MATCH (p:Paintings)-[r:in_COLLECTION]->(c:Collection) where c.name ='{0}' RETURN p.name limit 3".format(i)
                   for i in entities]

        elif question_type == 'collection_size':
            sql = ["MATCH (p:Collection) where p.name ='{0}' RETURN p.collection_size ".format(i)
                   for i in entities]

        elif question_type == 'collection_image':
            sql = ["MATCH (p:Collection) where p.name ='{0}' RETURN p.img ".format(i)
                   for i in entities]

        elif question_type == 'collection_date':
            sql = ["MATCH (p:Collection) where p.name ='{0}' RETURN p.date ".format(i)
                   for i in entities]

        elif question_type == 'collection_visitor':
            sql = ["MATCH (p:Collection) where p.name ='{0}' RETURN p.visitor_per_year ".format(i)
                   for i in entities]

        elif question_type == 'collection_description':
            sql = ["MATCH (p:Collection) where p.name ='{0}' RETURN p.website ".format(i)
                   for i in entities]

        elif question_type == 'genre_paintings':
            sql = ["MATCH (p:Paintings)-[r:has_GENRE]->(c:Genre) where c.name ='{0}' RETURN p.name limit 3 ".format(i)
                   for i in entities]

        elif question_type == 'depicts_paintings':
            sql = ["MATCH (p:Paintings)-[r:has_KEYWORD]->(c:Depicts) where c.name ='{0}' RETURN p.name limit 3 ".format(i)
                   for i in entities]

        elif question_type == 'creator_description':
            sql = ["MATCH (p:Person) where p.name ='{0}' RETURN p.uri ".format(i)
                   for i in entities]
        return sql
