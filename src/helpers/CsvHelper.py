import csv


def write_results(urlResult):
    """
    :param: filepath where to write the result to
    :param: list (including list of lists)(default [])
    :return: boolean (depending on success)
    """
    with open('results.csv', "a+", newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', dialect='excel')

        columns = read_file('sites.csv')
        columns.insert(0, 'URL')
        columns.insert(len(columns), "WordCount")
        columns.insert(len(columns), "PageCount")

        writer.writerow(columns)

        values = urlResult.csv_format()
        writer.writerow(values)


def write_index(index):
    with open('index.csv', "a+", newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ', dialect='excel')
        writer.writerow(index)


def read_results():
    """
    :param: takes the filepath as input for which file to read
    :return: returns the entire csv as list of lists
    """
    result = []
    with open('results.csv') as csvfile:
        data = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in data:
            result.append(row[0])
    return result

def read_classification_results():
    """
    :param: takes the filepath as input for which file to read
    :return: returns the entire csv as list of lists
    """
    result = []
    with open('../category/csv/resultstest.csv') as csvfile:
        data = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in data:
            result.append(row)
    return result


def write_file(filePath, data):
    with open(filePath, 'w') as file:
        for item in data:
            file.write("%s\n" % item)


def read_file(filePath):
    """
    :return: returns all the words which to crawl
    """
    result = []
    with open(filePath) as csvfile:
        data = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in data:
            result.append(row)
    data = [item for sublist in result for item in sublist]
    data.sort()

    return data

def get_classification_names():
    keys = []
    values = []
    with open('../category/csv/mapping.csv') as csvfile:
        data = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in data:
            keys.append(row[0])
            values.append(row[1])
    return dict(zip(keys, values))