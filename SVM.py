import sys
import numpy as np
from sklearn import svm

# This function returns a map from the query ID to a list of lists, each list in the larger list
# being a features list for each document corresponding to the query ID
def extract_features_from_file(file_path):
    query_doc_feature_map = {}
    training_file = open(file_path, 'rU')
    for line in training_file:
        feature_list = line.split(' ')

        # The relevance would appear as the first entity when parsed in this manner.
        # The relevance is later added into a separate list and the actual features into another while
        # generating the pairwise feature lists.
        relevance = feature_list[0]

        # Gets the query ID
        query_ID  = (feature_list[1].split(':'))[1]

        # This list maintains the list of features along with the relevance
        list_of_features = []

        list_of_features.append(relevance)

        # The query ID is not added in to the list, so the traversing begins from index 2
        for feature in feature_list[2:-1]:
            feature_value = (feature.split(':'))[1]
            list_of_features.append(feature_value)

        if query_doc_feature_map.get(query_ID) != None:
            query_doc_feature_map[query_ID].append(list_of_features)
        else:
            query_doc_feature_map[query_ID] = [list_of_features]
    return query_doc_feature_map

# This function parses the query feature map obtained from the extract_features_from_file function
# and generates pairwise feature lists for each document pair. A relevance list whose elements are
# +1/-1 (corresponding to the relative relevance of the document pair is also generated. These are
# then passed as the arguments to the SVM
def generate_pairwise_map(query_doc_feature_map):
    relevance_list = []
    query_pairwise_relative_feature_list = []
    for query_ID in query_doc_feature_map:
        list_of_feature_list = query_doc_feature_map[query_ID]
        for i in range(0, len(list_of_feature_list)):
            for j in range(0, len(list_of_feature_list)):
                if list_of_feature_list[i][0] == list_of_feature_list[j][0]:
                    continue
                else:
                    feature_list_difference = list(np.array(list_of_feature_list[i], dtype=np.float) - np.array(list_of_feature_list[j], dtype=np.float))
                    feature_list_difference[0] = 1 if feature_list_difference[0] > 0 else -1
                    relevance_list.append(feature_list_difference[0])
                    relative_feature_list = feature_list_difference[1:]
                    query_pairwise_relative_feature_list.append(relative_feature_list)
    return (query_pairwise_relative_feature_list, relevance_list)

# The SVM is trained in this method using the training data file. A linear kernel is being used for ranking.
# The linear classifier is returned.
def run_SVM(query_pairwise_relative_feature_list, relevance_list, penalty_factor):
    linear_classifier = svm.LinearSVC(C=penalty_factor)
    linear_classifier.fit(query_pairwise_relative_feature_list, relevance_list)
    return linear_classifier

# The classifier generated by the run_SVM method is tested here using the testing data file.
# Returns the accuracy of the classifier based on the correct predictions.
def test_SVM(linear_classifier, query_pairwise_relative_feature_list, relevance_list):
    number_of_correct_predictions = 0
    classifier_output = linear_classifier.predict(query_pairwise_relative_feature_list)
    for i in range(0, len(relevance_list)):
        if (relevance_list[i] == classifier_output[i]):
            number_of_correct_predictions += 1
    prediction_accuracy = 1.0*number_of_correct_predictions/len(relevance_list)
    return prediction_accuracy

def main():

    # Expects the training data file and the testing data file. Returns an error if either of the files is missing.
    if len(sys.argv) < 3:
        print 'Incorrect usage: Training or Test Data Set missing'
        print 'Usage: python SVM.py <training_set> <test_set>'
        exit(1)

    file_path = sys.argv[1]
    test_path = sys.argv[2]

    # The features are extracted from the training file.
    training_query_doc_feature_map = extract_features_from_file(file_path)

    # The query feature map generated is passed into the generate_pairwise_map function to generate the pairwise feature list and the relevance list.
    (training_query_pairwise_relative_feature_list, training_query_relevance_list) = generate_pairwise_map(training_query_doc_feature_map)

    # The penalty factor is initialized to 0.5. The classifiers are generated for penalty factors in the range [0.5 - 50], with the penalty factor
    # incremented by 0.5 in each iteration.
    penalty_factor = 0.5

    # Stores the maximum prediction accuracy.
    max_prediction_accuracy = 0
    max_penalty_factor = 0

    while penalty_factor <= 50:

        # Generates classifier corresponding to the current penalty factor.
        linear_classifier = run_SVM(training_query_pairwise_relative_feature_list, training_query_relevance_list, penalty_factor)

        # Extracts features from the test file and creates a query-feature map
        testing_query_doc_feature_map = extract_features_from_file(test_path)

        # Creates pairwise relative feature list and the relevance list for the testing data
        (testing_query_pairwise_relative_feature_list, testing_query_relevance_list) = generate_pairwise_map(testing_query_doc_feature_map)

        # Tests the SVM for the testing data and gets the prediction accuracy
        prediction_accuracy = test_SVM(linear_classifier, testing_query_pairwise_relative_feature_list, testing_query_relevance_list)

        # Logic to maintain maximum prediction accuracy and the corresponding classifier
        if prediction_accuracy > max_prediction_accuracy:
            max_prediction_accuracy = prediction_accuracy
            max_penalty_factor = penalty_factor
            best_classifier = linear_classifier

        penalty_factor += 0.5

    # Reports the accuracy and the top 10 features (based on the absolute weights)
    print 'Accuracy of prediction on the test set: '+ str(max_prediction_accuracy * 100.0) + ' %'
    print ''
    print 'Top 10 features'
    print '==============='
    feature_weight_list = best_classifier.coef_[0]
    for feature_index in reversed(np.argsort(np.absolute(np.array(feature_weight_list)))[-10:]):
        print 'Feature '+ str(feature_index + 1) + ', Score: '+ str(feature_weight_list[feature_index])

if __name__ == '__main__':
    main()

