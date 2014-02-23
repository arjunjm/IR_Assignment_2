import sys
import numpy as np
from sklearn import svm

def extract_features_from_file(file_path):
    query_doc_feature_map = {}
    training_file = open(file_path, 'rU')
    for line in training_file:
        feature_list = line.split(' ')
        relevance = feature_list[0]
        query_ID  = (feature_list[1].split(':'))[1]

        list_of_features = []
        list_of_features.append(relevance)
        for feature in feature_list[2:-1]:
            feature_value = (feature.split(':'))[1]
            list_of_features.append(feature_value)

        if query_doc_feature_map.get(query_ID) != None:
            query_doc_feature_map[query_ID].append(list_of_features)
        else:
            query_doc_feature_map[query_ID] = [list_of_features]
    return query_doc_feature_map

def generate_pairwise_map(query_doc_feature_map):
    #global query_doc_feature_map
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

def run_SVM(query_pairwise_relative_feature_list, relevance_list):
    linear_classifier = svm.LinearSVC(C=0.5)
    linear_classifier.fit(query_pairwise_relative_feature_list, relevance_list)
    return linear_classifier

def test_SVM(linear_classifier, query_pairwise_relative_feature_list, relevance_list):
    number_of_correct_predictions = 0
    classifier_output = linear_classifier.predict(query_pairwise_relative_feature_list)
    for i in range(0, len(relevance_list)):
        if (relevance_list[i] == classifier_output[i]):
            number_of_correct_predictions += 1
    prediction_accuracy = 1.0*number_of_correct_predictions/len(relevance_list)
    return prediction_accuracy

def main():
    file_path = sys.argv[1]
    training_query_doc_feature_map = extract_features_from_file(file_path)
    (training_query_pairwise_relative_feature_list, training_query_relevance_list) = generate_pairwise_map(training_query_doc_feature_map)

    linear_classifier = run_SVM(training_query_pairwise_relative_feature_list, training_query_relevance_list)

    testing_query_doc_feature_map = extract_features_from_file('test.txt')
    (testing_query_pairwise_relative_feature_list, testing_query_relevance_list) = generate_pairwise_map(testing_query_doc_feature_map)
    prediction_accuracy = test_SVM(linear_classifier, testing_query_pairwise_relative_feature_list, testing_query_relevance_list)

    print 'Prediction Accuracy ='+str(prediction_accuracy)

if __name__ == '__main__':
    main()

