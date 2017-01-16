import pandas as pd

""""Helper class for processing data that needs to be loaded into the machine learning algorithm"""

""""Get the raw learning data as a Pandas DataFrame from the csv files based on if the machine learning
algorithm needs to check scope vs no-scope or website vs web shop"""


def get_raw_data(check_scope):
    # Load csv files
    if check_scope:
        positive = pd.read_csv("../ml/csv/scope.csv", delimiter=';')
        negative = pd.read_csv("../ml/csv/noscope.csv", delimiter=';')
    else:
        positive = pd.read_csv("../ml/csv/webshops.csv", delimiter=';')
        negative = pd.read_csv("../ml/csv/nonwebshops.csv", delimiter=';')

    scope_length = len(positive)

    # Combine into one DataFrame
    data = pd.concat([positive, negative], ignore_index=True)
    data['Label'] = 0

    # Add label based on if the data represents a positive or negative result.
    for index, row in data.iterrows():
        label = 1 if index < scope_length else 0
        data.set_value(index, 'Label', label)

    return data


""""Get the data for website vs web shop checking"""


def get_scope_data():
    return get_raw_data(True)


""""Get the data for scope vs no-scope checking"""


def get_webshop_data():
    return get_raw_data(False)


""""Get the data for category checking"""


def get_classify_data():
    return pd.read_csv("../category/csv/results.csv", delimiter=';')


""""Divide by method for the PageCount column"""


def remove_columns(data):
    del data[-1]
    del data[-1]
    del data[0]

    return data
