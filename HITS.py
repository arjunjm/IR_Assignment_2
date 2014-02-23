import networkx as nx
import sys
import cjson

user_graph = nx.DiGraph()

def make_graph(file_path):
    global user_graph
    tweet_file = open(file_path, 'rU')
    for line in tweet_file:
        decoded_tweet = cjson.decode(line)

        # Gets tweet user name
        tweet_user_name = decoded_tweet['user']['screen_name']

        # Adds the tweet user name to the graph
        if not user_graph.has_node(tweet_user_name):
            user_graph.add_node(tweet_user_name)

        # Gets mentions in the tweet
        tweet_entities_list = decoded_tweet['entities']['user_mentions']

        for entities in tweet_entities_list:
            mentioned_user_screen_name = entities['screen_name']
            # Adds the mentioned user name to the graph if it does not exist already.
            if not user_graph.has_node(mentioned_user_screen_name):
                user_graph.add_node(mentioned_user_screen_name)

            # Checks if the mentioned user name is not the same as the tweet author's name and adds the edge to the graph if it does not exist already.
            if (tweet_user_name != mentioned_user_screen_name) and (not (user_graph.has_edge(tweet_user_name, mentioned_user_screen_name))):
                user_graph.add_edge(tweet_user_name, mentioned_user_screen_name)

def normalize(input_dict):
    sum_of_values = 0.0

    # Calculate the sum of values
    for key in input_dict.keys():
        sum_of_values += input_dict[key]

    # Divide each term by the sum of values
    for key in input_dict.keys():
        input_dict[key] = input_dict[key]/sum_of_values

    return input_dict

def run_hits_algorithm(connected_graph):

    # This variable keeps track of the number of times the HITS algorithm is repeated.
    loop_count = 0

    # The counter dictionaries for keeping track of hub scores
    hub_score_counter = {}
    temp_hub_score_counter = {}

    # The counter dictionaries for keeping track of authority scores
    authority_score_counter = {}
    temp_authority_score_counter = {}

    # Initializing the hub and authority scores of every node to 1
    for node in connected_graph.nodes():
        hub_score_counter[node] = 1.0
        authority_score_counter[node] = 1.0

    while True:
        for node in connected_graph.nodes():

            #Gets the list of outgoing nodes
            successor_nodes = connected_graph.successors(node)

            #Gets the list of incoming nodes
            predecessor_nodes = connected_graph.predecessors(node)

            temp_hub_score_counter[node] = 0.0
            temp_authority_score_counter[node] = 0.0

            # Computes the new hub scores based on the authority scores in the previous iteration
            for out_node in successor_nodes:
                temp_hub_score_counter[node] += authority_score_counter[out_node]

            # Computes the new authority scores based on the hub scores in the previous iteration
            for in_node in predecessor_nodes:
                temp_authority_score_counter[node] += hub_score_counter[in_node]

        for node in connected_graph.nodes():
            hub_score_counter[node] = temp_hub_score_counter[node]
            authority_score_counter[node] = temp_authority_score_counter[node]

        # Normalizes the hub scores
        hub_score_counter = normalize(hub_score_counter)

        # Normalizes the authority scores
        authority_score_counter = normalize(authority_score_counter)

        # The loop is run for 300 iterations. The hub and authorities values would have converged by now.
        loop_count += 1
        if loop_count > 300:
            break

    return (hub_score_counter, authority_score_counter)

def main():
    file_path = sys.argv[1]
    global user_graph

    # Constructs the graph based on the dataset
    make_graph(file_path)

    # Get the weakly connected graph components. HITS is to be run on the largest of such components.
    weakly_connected_graph_components = nx.weakly_connected_component_subgraphs(user_graph)

    # Get the largest weekly connected graph component
    largest_weakly_connected_graph = weakly_connected_graph_components[0]

    (hub_score_counter, authority_score_counter) = run_hits_algorithm(largest_weakly_connected_graph)

    # Sort the lists
    sorted_hub_score_list = sorted(hub_score_counter.items(), key = lambda item: item[1], reverse = True)
    sorted_authority_score_list = sorted(authority_score_counter.items(), key = lambda item: item[1], reverse = True)

    # Print top 20 hubs
    print "Top 20 Hubs"
    print "==========="
    for i in range(0, 20):
        if sorted_hub_score_list[i] != None:
            print sorted_hub_score_list[i][0]

    print ""

    # Print top 20 authorities
    print "Top 20 Authorities"
    print "=================="
    for i in range(0, 20):
        if sorted_authority_score_list[i] != None:
            print sorted_authority_score_list[i][0]

if __name__ == '__main__':
    main()

