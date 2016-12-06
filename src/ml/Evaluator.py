from sklearn import metrics

""""Train the data with the given algorithm
    This method will then print a number of arguments regarding the accuracy of the algorithm"""


def train_and_evaluate(clf, X_train, X_test, y_train, y_test):
    clf.fit(X_train, y_train)

    #print("Accuracy on training set:")
    #print(clf.score(X_train, y_train))
    #print("Accuracy on testing set:")

    lel = clf.score(X_test, y_test)

    #print(clf.score(X_test, y_test))

    #y_pred = clf.predict(X_test)

    #print("Classification Report:")
    #print(metrics.classification_report(y_test, y_pred))
    #print("Confusion Matrix:")
    #print(metrics.confusion_matrix(y_test, y_pred))

    return lel
