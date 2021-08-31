import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import pdist
def get_similarity(name,label =None):
    embedding = pd.read_csv("component/export.csv")
    embedding = embedding[((embedding.label != '[]')&(embedding.embedding!='[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]'))]
    name = name.strip()
    embedding['embedding'] = embedding.apply(lambda row : eval(row['embedding']), axis = 1)
    if label:
        if label == 'Exhibit':
            label = 'Paintings'
        # if label is specify, then we return the items of that kind of label
        test = list(embedding[(embedding.name == name)].embedding)
        curent_id = int(embedding[(embedding.name == name)].nodeId)
        similarity_score = []
        for index, row in embedding.iterrows():
            Vec = np.vstack([test, row.embedding])
            dist2 = 1 - pdist(Vec, 'cosine')
            similarity_score.append(dist2)
        embedding['similarity'] = similarity_score
        sorted_df = embedding[((embedding.label == '['+label+']') & (embedding.nodeId != curent_id) )].sort_values("similarity",
                                                                                                           ascending=False)

        return sorted_df.iloc[0].nodeId
    else:
        # if label is not specify, then we return the items with same label
        test = list(embedding[(embedding.name == name)].embedding.item())
        curent_id = int(embedding[(embedding.name == name)].nodeId.item())
        label = embedding[(embedding.name == name)].label.item()
        print('label is', label)
        similarity_score = []
        for index, row in embedding.iterrows():
            Vec = np.vstack([test, row.embedding])
            dist2 = 1 - pdist(Vec, 'cosine')
            similarity_score.append(dist2)
        embedding['similarity'] = similarity_score
        sorted_df = embedding[((embedding.label == label)&(embedding.nodeId != curent_id))].sort_values("similarity",ascending=False)
        # print(sorted_df)
        return sorted_df.iloc[0].nodeId

print(get_similarity(' Hendrik Heerschop',label='Exhibit'))
