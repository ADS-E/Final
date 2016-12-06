from sklearn.cross_validation import train_test_split


def create_sets(data):
    columns = data.columns.tolist()
    X = data[columns[1:-1]]
    y = data['Label']

    return train_test_split(X, y, test_size=0.25, random_state=33)
