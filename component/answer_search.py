from py2neo import Graph
from component.question_classfier import *
from component.question_parser import *

class AnswerSearch:
    def __init__(self):
        self.g = Graph(
            scheme="bolt",
            host="localhost",
            port=7687,
            auth=("neo4j", "000000"))
        self.num_limit = 20
        self.classifier = QuestionClassifier()
        self.parser = QuestionPaser()

    def answer_prettify(self, question):
        data = self.classifier.classify(question)
        print('classified question is:',data)
        try:

            sqls = self.parser.parser_main(data)
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


if __name__ == '__main__':
    handler = AnswerSearch()
    while 1:
        question = input('input an question:')
        answer = handler.answer_prettify(question)
        print(answer)
