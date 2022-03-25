from os import remove
from pkgutil import get_data
from networkx.algorithms.shortest_paths.generic import shortest_path
import api
import networkx as nx
import time


class Tree:
    def __init__(self):
        """
            Initialise the graph and values
        """
        self.G = nx.Graph()
        self.q = []
        self.g = []
        self.last_save = 0

        self.generations = 5

    def load(self):
        """
            Try to load the graph. If this is unsuccesfull,
            it will initialize a new graph with Gerolf of Holland.
        """
        try:
            self.G = nx.read_graphml("G.graphml")
            fq = open("q.txt", "r")
            Linesq = fq.readlines()
            fq.close()
            for line in Linesq:
                self.q.append(int(line.strip()))

            fg = open("g.txt", "r")
            Linesg = fg.readlines()
            fg.close()
            for line in Linesg:
                self.g.append(int(line.strip()))
        except:
            print("Loading unsuccesful, initializing with Gerolf")
            self.G.add_node("Q708703", name="Gerolf of Holland")
            self.q = [int("708703")]
            self.g = [int("708703")]

    def reset(self):
        """
            Reset the the graph and the queue.
        """
        try:
            remove("G.graphml")
            remove("g.txt")
            remove("q.txt")
        except:
            return 0


    def get_data(self):
        """
            Make a query with some person at its center. Then use this query
            to get the relatives.
        """

        #Get the relatives.
        main = "Q" + str(self.q.pop(0))
        result = api.fetch(main, self.generations)
        print(self.G.number_of_nodes())
        print(result[0])

        #Save every 1000 nodes.
        if len(result) == 1:
            self.last_save = self.G.number_of_nodes()
            self.save()

        if self.G.number_of_nodes() - self.last_save > 1000:
            self.last_save = self.G.number_of_nodes()
            self.save()

        #Add the new nodes to the graph.
        for i in range(1, len(result)):

            #Get the codes and names of every relative.
            codes = [result[i][0][j] for j in range(self.generations)]
            names = [result[i][1][j] for j in range(self.generations)]
            all = [main]

            #Add all codes to a list.
            for j in range(self.generations):
                #If a code is invalid, don't use it.
                if codes[j][0] != "Q":
                    codes[j] = codes[j-1]
                all.append(codes[j])

            #Add the node to the graph if it is new.
            for j in range(self.generations - 1):
                if self.bni(self.g, self.toInt(codes[j])) == 0:
                    self.G.add_node(codes[j], name=names[j])

            #Add the last relative to the graph if it is new.
            #If the every relative in the list is unique, also add it to q.
            if self.bni(self.g, self.toInt(codes[self.generations - 1])) == 0:
                self.G.add_node(codes[self.generations - 1], name=names[self.generations - 1])
                if len(all) == len(set(all)):
                    self.bni(self.q, self.toInt(codes[self.generations - 1]))

            #Add an edge between different relatives
            for j in range(self.generations):
                if all[j] != all[j+1]:
                    self.G.add_edge(all[j], all[j+1])

            #Remove duplicates from the queue
            for j in range(self.generations - 1):
                self.bnr(self.q, self.toInt(codes[j]))

        #Wait before the next query.
        time.sleep(5)
        return 0


    def expand(self):
        """
            Expand the graph until we interrupt, then save.
        """
        try:
            while True:
                self.get_data()
        except KeyboardInterrupt:
            self.save()



    def save(self):
        """
            Save the graph, queue, and list of nodes.
        """
        #Save the graph.
        nx.write_graphml(self.G, "G.graphml")

        #Save the queue.
        f = open("q.txt", "w")
        for i in range(len(self.q)):
            f.write(str(self.q[i]) + "\n")
        f.close()

        #Save the list of nodes.
        f = open("g.txt", "w")
        for i in range(len(self.g)):
            f.write(str(self.g[i]) + "\n")
        f.close()


    def bfs(self, G, start, end):
        """
            Do a breadth-first search to find the shortest path.
            Return the names in that path.
        """
        nodes = shortest_path(G, start, end)
        print(nodes)
        names = [G.nodes[nodes[i]]['name'] for i in range(len(nodes))]
        return names

    def toInt(self, s):
        """
            Convert a code to an integer.
        """
        return int(s.replace("Q",""))


    def bni(self, q, e):
        """
            Perform a binary insert to add a number to the queue or
            to the list of nodes.
        """
        if len(q) == 0:
            q.append(e)

        L = 0
        R = len(q) - 1
        m = (L+R)//2
        while L <= R:
            m = (L+R)//2

            #Remove the half that does not include e.
            if q[m] < e:
                L = m + 1
            elif q[m] > e:
                R = m - 1
            else:
                return 1

        #Insert in the right place
        if q[m] < e:
            q.insert(m+1, e)
        else:
            q.insert(m,e)

        return 0

    def bnr(self, q, e):
        """
            Perform a binary remove on an item from a list.
        """
        L = 0
        R = len(q) - 1
        m = (L+R)//2
        while L <= R:
            m = (L+R)//2

            if q[m] < e:
                L = m + 1
            elif q[m] > e:
                R = m - 1
            elif q[m] == e:
                del q[m]
                return 0
        return 1


tree = Tree()
tree.load()
#tree.expand()
#print(tree.bfs(tree.G, "Q346", "Q111320602"))

""" degrees = [val for (_, val) in tree.G.degree()]
bar = []
for i in tree.G.degree():
    if i[1] == 0:
        print(i[0])

for i in range(max(degrees) + 1):
    bar.append(degrees.count(i))
print(bar) """

for n in tree.G.nodes():
    print(n)

#nx.draw(G)