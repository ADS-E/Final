from sklearn.cross_validation import train_test_split


def create_sets(data):
    columns = data.columns.tolist()[1:-3]
    l = len(columns)
    X = data[columns]
    y = data['Label']

    X = feature_selection(X,y)
    return train_test_split(X, y, test_size=0.25, random_state=33)

def feature_selection(X,y):
    sel = SelectKBest(k=10)
    return sel.fit_transform(X,y)