import csv


def write_index(index):
    with open('index.csv', "a+", newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ', dialect='excel')
        writer.writerow(index)


""" Read the classification results for categorization from a file corresponding to the given file path.
Returns the entire csv as list of lists"""


def read_classification_results():
    result = []
    with open('../category/csv/resultstest.csv') as csvfile:
        data = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in data:
            result.append(row)
    return result


""""Get the category names and corresponding ids as a dictionary"""


def get_classification_names():
    keys = []
    values = []
    with open('../category/csv/mapping.csv') as csvfile:
        data = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in data:
            keys.append(row[0])
            values.append(row[1])
    return dict(zip(keys, values))


"""Write given data to a file corresponding to the given file path."""


def write_file(file_path, data):
    with open(file_path, 'w') as file:
        for item in data:
            file.write("%s\n" % item)


"""Read a file corresponding to the given file path.
Return the content of the file"""


def read_file(file_path):
    result = []
    with open(file_path) as csvfile:
        data = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in data:
            result.append(row)
    data = [item for sublist in result for item in sublist]
    data.sort()

    return data
