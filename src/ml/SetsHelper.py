from sklearn.cross_validation import train_test_split
from sklearn.feature_selection import SelectKBest

""""Class providing helper methods for data that needs to be fed into the machine learning algorithm"""


def create_sets(data):
    columns = data.columns.tolist()[1:-3]
    l = len(columns)
    X = data[columns]
    y = data['Label']

    # X = feature_selection(X,y)
    return train_test_split(X, y, test_size=0.25, random_state=33)


""""Apply KBest"""


def feature_selection(X, y):
    sel = SelectKBest(k=10)
    return sel.fit_transform(X, y)
