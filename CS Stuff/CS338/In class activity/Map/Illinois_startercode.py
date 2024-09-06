"""
Andrew Shallue, CS338 activity, Spring 2023

Searching on a map of Illinois
"""
# documentation for queue package:  https://docs.python.org/3/library/queue.html
import queue
import collections

# map implemented as a graph with nodes and edges
# for a visual representation see IllinoisMap.pdf
class Map:
    def __init__(self):
        self.nodes = []
        self.nodes.append(City("chicago", [("rockford", 90), ("bloomington", 135), ("champaign", 130) ]))
        self.nodes.append(City("rockford", [("chicago", 90), ("bloomington", 135), ("rock island", 125)]))
        self.nodes.append(City("rock island", [("rockford", 125), ("peoria", 100)]))
        self.nodes.append(City("peoria", [("rock island", 100), ("bloomington", 40), ("springfield", 75)]))
        self.nodes.append(City("bloomington", [("peoria", 40), ("rockford", 135), ("chicago", 135), ("champaign", 50), ("springfield", 70)]))
        self.nodes.append(City("champaign", [("chicago", 130), ("bloomington", 50), ("effingham", 80)]))
        self.nodes.append(City("effingham", [("champaign", 80), ("springfield", 90), ("cairo", 175)]))
        self.nodes.append(City("springfield", [("peoria", 75), ("bloomington", 70), ("effingham", 90), ("st louis", 100)]))
        self.nodes.append(City("st louis", [("springfield", 100), ("cairo", 150)]))
        self.nodes.append(City("cairo", [("st louis", 150), ("effingham", 175)]))

    # given a city name, return the City object that has that name
    # note that if name is not the list, NoneType is returned
    def find_city(self, given_name):
        for city in self.nodes:
            if city.name == given_name:
                return city


# each city represented by its name and its neighbors
# neighbors is a list of pairs, where each pair is (neighbor_name, distanct_to_neighbor)
class City:
    def __init__(self, name_in, neighbors_pairs):
        self.name = name_in
        self.neighbors = neighbors_pairs

# agent can move to adjacent cities, can execute a plan
class Agent:
    def __init__(self, start):
        self.location = start
        self.distance_moved = 0
        self.location_path_hash = {}    # hash table used for bidirectional search

    # move to an adjacent city and update distance_moved
    # if given city name is not adjacent, agent is not moved
    def move_adjacent(self, new_city, env):
        # first find the city object for the agent's current location
        current_city = env.find_city(self.location)

        # now check adjacent cities to find the new city
        for pair in current_city.neighbors:
            if pair[0] == new_city:
                self.location = new_city
                self.distance_moved += pair[1]
        
    # given a list of cities which is a planned route, execute that route
    # return the distance traveled
    def execute_plan(self, city_list, env):
        # simply move to each new city in turn
        for city_name in city_list:
            self.move_adjacent(city_name, env)

        return self.distance_moved

    # first attempt at bfs, very bad
    # no explored set, and not copying the path means the pathing is all messed up
    def bad_bfs(self, goal_city, map):
        # set up the queue, seed with initial city
        # I will store a pair: (name, path), not the city object
        frontier = queue.Queue()
        init_pair = (self.location, [])
        frontier.put(init_pair)

        #continue until queue is empty or goal city found
        while not frontier.empty():
        
            # pop the city on the front
            current_pair = frontier.get()
            current_city = current_pair[0]
            current_path = current_pair[1]

            # check if it is the solution
            if current_city == goal_city:
                return current_path

            # if not, go through adjacent cities and push onto queue with updated paths
            else:
                city_ob = map.find_city(current_city)
                for adj_pairs in city_ob.neighbors:

                    # the name is the first part of the pair
                    new_name = adj_pairs[0]
                    new_path = current_path
                    new_path.append(new_name)
                  
                    frontier.put( (new_name, new_path) )

         # if the while loop ended without a solution, return empty as failure
        return []

    


def main():
    print("Hello world")
    M = Map()
    A = Agent("rock island")
    plan = A.bad_bfs("cairo", M)
    d = A.execute_plan(plan, M)
    print("distance traveled", d)
    print("plan executed:", plan)
    print()


if __name__ == '__main__':
	main()
        
