import json

class Rule :
    def __init__ (self, label, premises, actions, conclusions) :
        self.label = label
        self.premises = premises
        self.actions = actions
        self.conclusions = conclusions
        self.adjs = []

    def __str__ (self) :
        join_fn = lambda l : ", ".join(l)
        return self.label + " : [ " + join_fn(self.premises) + " ] --[ " + join_fn(self.actions) + " ]-> [ " + join_fn(self.conclusions) + " ]"
    
    def printable (self) : return True

class Attacker :
    def __init__ (self, label, fact, printable=False) :
        if label == "Send" :
            label = "AttSend"
            printable = True
        elif label == "Recv" : label = "AttRecv"
        self.label = label
        self.fact = fact
        self._printable = printable
        self.adjs = []

    def __str__ (self) :
        return self.label + " : " + self.fact
    
    def printable (self) : return self._printable
    
def topological_sort(graph):
    # Function to perform a depth-first search and record the order
    def dfs(node, visited, stack):
        visited.add(node)
        for neighbor in graph[node].adjs:
            if neighbor not in visited:
                dfs(neighbor, visited, stack)
        stack.append(node)

    visited = set()  # Set to keep track of visited nodes
    stack = []  # Stack to store the topological order
    # Perform DFS for each node in the graph
    for node in graph:
        if node not in visited:
            dfs(node, visited, stack)

    # Reverse the stack to get the topological order
    stack.reverse()
    return stack    
    
# Only function to use externally to this module
# It takes a string containing a path to a valid .json file exported by Tamarin as input and the list of lemma names
# And produces a dictionary of strings, containing the topological sorts of the Tamarin traces, labelled by their relative lemma's name
def read_traces (path, lemma_names) :

    # Open the input file and read it as dictionary (throws error if the syntax is not correct)
    with open(path, "r") as f :
        traces_data = json.load(f)["graphs"]
    
    # Throw an error if there are no graphs to parse
    if len(traces_data) == 0 : raise Exception ("Error: No valid traces to parse")

    # Extract the traces and return a dictionary with the topologically-sorted traces as values and the lemmanames as keys
    return { ln : __extract_trace(td) for td in traces_data for ln in lemma_names if ln in td["jgLabel"] }

# This function is not meant to be used outside of this module
# Given the output
def __extract_trace (data, simplified=True) :
    # Save the graph as a dictionary of nodes. The key is the timestamp (id) of the node
    graph = dict()
    # Save the out facts to perform graph simplification. This dictionary saves, for each id of an Out fact, its corresponding term
    out_facts = dict()

    # Extract the nodes from the data dictionary
    for node in data["jgNodes"] :
        node_id = node["jgnId"]
        node_label = node["jgnLabel"]
        node_data = node["jgnMetadata"]
        if node["jgnType"] == "isProtocolRule" :
            node_premises = [ prem["jgnFactShow"] for prem in node_data["jgnPrems"] ]
            node_actions = [ act["jgnFactShow"] for act in node_data["jgnActs"] ]
            node_conclusions = [ conc["jgnFactShow"] for conc in node_data["jgnConcs"] ]
            # Keep track of all the Out facts for later graph simplification
            for conc in node_data["jgnConcs"] :
                if conc["jgnFactName"] == "Out" : out_facts[ conc["jgnFactId"] ] = conc["jgnFactShow"][5:-2]
            graph[node_id] = Rule(node_label, node_premises, node_actions, node_conclusions)
        else :
            if len(node_data["jgnActs"]) > 0 :
                node_fact = node_data["jgnActs"][0]["jgnFactShow"]
            else :
                node_fact = node_data["jgnConcs"][0]["jgnFactShow"]
            graph[node_id] = Attacker(node_label, node_fact)
    
    # Construct the graph, keeping track of an additional counter to introduce new nodes for graph simplification
    new_node = 0
    for edge in data["jgEdges"] :
        source = edge["jgeSource"]
        target = edge["jgeTarget"].split(":")[0]
        # If an edge e connects an Out fact N1 to another action N2, introduce a new node N with a Recv action such that N is a proxy between N1 and N2. In practice, we update N1 -> N2 to N1 -> N -> N2
        if source in out_facts :
            new_target = str(new_node)
            new_node += 1
            # Create N as an Attacker action. Make it printable so that it will appear in the simplified trace
            graph[new_target] = Attacker("AttRecv", out_facts[source], True)
            graph[source.split(":")[0]].adjs.append(new_target)
            graph[new_target].adjs.append(target)
        else :
            source = source.split(":")[0]
            graph[source].adjs.append(target)

    # The trace is a Directed Acyclic Graph, so we can provide a sequential representation that preserves dependency relations by computing a topological sort of the nodes
    return [ str(graph[idx]) for idx in topological_sort(graph) if graph[idx].printable() or not simplified ]