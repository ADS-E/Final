import pandas as pd


def get_raw_data():
    scope = pd.read_csv("../ml/csv/webshops.csv", delimiter=';')
    no_scope = pd.read_csv("../ml/csv/nonwebshops.csv", delimiter=';')

    scope_length = len(scope)

    data = pd.concat([scope, no_scope], ignore_index=True)
    data['Label'] = 0

    for index, row in data.iterrows():
        label = 1 if index < scope_length else 0
        data.set_value(index, 'Label', label)

    # data = data.iloc[np.random.permutation(len(data))]
    #print(data)

    return data


def get_data():
    data = get_raw_data()
    # data = data.applymap(lel)

    # print(data)

    return data


def divided_by_page():
    return divide_by('PageCount')


def divided_by_word():
    return divide_by('WordCount')


def divide_by(value):
    data = get_raw_data()

    for column in data.columns.tolist()[1:-3]:
        data[column] = data[column] / data[value]

    return lel(data)


def drop_columns(data):
    # data = data.drop('PageCount', 1)
    # data = data.drop('WordCount', 1)
    # data = data.drop('URL', 1)

    return data


def divide_one(value, list):
    page_count = list[-1]
    word_count = list[-2]

    del list[-1]
    del list[-1]
    del list[0]

    for ele, i in enumerate(list):
        if value is 'PageCount':
            list[i] = ele / page_count
        elif value is 'WordCount':
            list[i] = ele / word_count

    return list


def lel(x):
    # that, if x is a string,
    if type(x) is str:
        # just returns it untouched
        return x
    # but, if not, return it multiplied by 100
    elif x:
        if x == 0.0:
            print('zerp')

        zero = x == 0
        value = 0 if zero else 1
        return value
    # and leave everything else
    else:
        return
