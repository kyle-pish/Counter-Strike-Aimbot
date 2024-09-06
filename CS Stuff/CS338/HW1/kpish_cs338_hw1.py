"""
Homework 1 starter code for CS338 (AI) - Andrew Shallue, Fall 2024
create an agent that can open boxes and detect if cake is in the boxes

Authors: Andrew Shallue, Kyle Pish
"""

"""
Written Homework Problems:

    1) Performance Measure: Ratio of the amount of dirt cleaned vs the number of moves made
               Environment: A line of n boxes
                 Actuators: Movement of the agent (left or right) and action of cleaning dirt
                   Sensors: Detecting if a box contains dirt

    2) In a stochastic environment the strategy that could potential result in the highest ratio of dirt : moves would be to stay in one spot
       Since the environment updates at random time intervals, it doesn't matter what the robot does, given enoough time, dirt will eventually spawn
       In this scenario there is a potential for an unlimited amount of dirt cleaned in 0 moves, granted this is not the fastest approach as the robot is just waiting around

       Another approach I believe would be effective would to begin by moving to the left square by square until reaching the begining of the line,
       then return to the original starting postion and move to the right square by square until reaching the end.
       Because every square begins with a 25% chance of dirt we want to make sure we check each of them.
       Now from this point we can have the robot jump to the start and move to the end repeatedly,
       The logic behind this is checking the squares that were checked the longest amount of time ago, meaning they have had the most time to potentially be filled with dirt
       For example, say there is a 10% change every 1 second for dirt to spawn in a given square and we have a line of 5 squares, the robot can check 1 square every second.
       After the initial sweep at the beginning, we move all the way through the line. once reaching the end, that means the first box has had a 10% chance 4 times, 
       meaning it has the highest probability to be filled

       Not sure how much sense that made so here is a silly little visual I created:
        https://docs.google.com/document/d/13gFU2SkXJ8OPNkbBfi4Sa813697ZFTSnxApwOMovWRA/edit?usp=sharing

       Adding on after our discussion in class on Tuesday September 3, Professor Shallue mentioned we should not have a "tourist" agent, meaning the agent should not just jump around.
       If this is the case, we could follow a similar strategy to staying in one spot, but this time the robot can start somewhere and constantly check it till dirt appears.
       Once the dirt appears it will clean it, but now instead of staying there, the robot will move to the next space. This ensures that the robot will still go over every square
       while also minimizing the amount of moves made, this should result in a ratio of 1 move per 1 square cleaned.
"""

"""
Coding Problems

    3)
        a) get_percept function

        b) move_agent function

        c) grab_cake function

        d) strategy function

"""
import random as rand

class Environment:
    def __init__(self, num_boxes):
        self.boxes = []

        # fill boxes with cake at probabilty 1/4
        for i in range(num_boxes):
            pull = rand.randint(0, 4)
            if pull == 0:
                self.boxes.append("cake")
            else:
                self.boxes.append("nothing")

class Agent:
    def __init__(self, start):
        self.position = start
        self.cake_eaten = 0
        self.boxes_opened = 0

    def get_percept(self, env):
        """
        Opening the box at the agents current position
        Increasing the number of boxes opened 
        returning what the agent finds

        Arguments: The environment
        """
        # Increase the number of boxes opened
        self.boxes_opened += 1 
        # Return what the agent 'sees' at current position
        return env.boxes[self.position]  

    def move_agent(self, new_pos):
        """
        Set agents position to the new_pos
        
        Arguments: new position
        """
        self.pos = new_pos # Update agents position

    def grab_cake(self, env):
        """
        Check the box at agents current position
        If there is cake -> grab it, update cakes, and set box to 'nothing'

        Arguments: The environment
        """
        # Check for cake and update appropriate counts
        if env.boxes[self.position] == "cake": 
            env.boxes[self.position] = "nothing"
            self.cake_eaten += 1

def strategy(env):
    """
    Create an agent at position 0 of the line of boxes
    Open boxes from left to right until:
    1 cake found or end of line reached

    The main idea of this strategy is that there is a high chance of a cake being within the first 4 boxes
    since the probability of cake is 1/4. This heavily relies on luck, but in theory if the agent can find
    a cake within the first 4 boxes and avoid opening unnecessary boxes, it will score much better

    Strategy designed with ideas provided by Andrew Shallue
    """
    
    agent = Agent(start=0)

    # Alternative while statement for robot to check all boxes
    # On average it is worse than my abort strategy
    # This was used for testing/comparision of performance
    '''while agent.position < len(env.boxes):'''
    
    # Execute while 1) agent hasn't found cake 2) agent isn't at the end
    while agent.cake_eaten == 0 and agent.position < len(env.boxes):
        percept = agent.get_percept(env)

        # If cake is found, call grab_cake
        if percept == "cake":
            agent.grab_cake(env)
            print(f"Cake eaten! Total cake eaten: {agent.cake_eaten}")

        # If no cake, move agent to the next box
        else:
            agent.position += 1
            agent.move_agent(agent.position)
            print(f"No cake, moving to position {agent.position}")
    
    # Return cake_eaten and boxes open for performance metric
    # Return the boxes to ensure everythin updates/functions properly
    return agent.cake_eaten, agent.boxes_opened, env.boxes

def main():
    num_trials = 100
    total_cake_eaten = 0
    total_boxes_opened = 0

    for trial in range(num_trials):
        # Create environment with 8 boxes
        env = Environment(num_boxes=8)

        # Mainly for testing, so we can compare the initial vs final
        initial_state = env.boxes.copy()

        # Call strategy with the created environment
        cake_eaten, boxes_opened, final_state = strategy(env)

        # Total count over 100 trials for cake and boxes
        total_cake_eaten += cake_eaten
        total_boxes_opened += boxes_opened

        # Output metrics to monitor each trial
        print("")
        print(f"Trial {trial + 1}:")
        print(f"Initial State: {initial_state}")
        print(f"Final State: {final_state}")
        print(f"Boxes Opened: {boxes_opened}")
        print(f"Cake Eaten: {cake_eaten}")
        print("")
    
    # Final performance metrics
    print(total_cake_eaten, " pieces of cake were eaten")
    print(total_boxes_opened, " boxes were opened")

    performance = total_cake_eaten / total_boxes_opened if total_boxes_opened > 0 else 0
    print(f"Overall Performance: {performance:.2f} (Total Cake Eaten / Total Boxes Opened)")

if __name__ == "__main__":
    main()

"""
Note on strategy:

The goal of the strategy to abort after finding 1 cake as mentioned above was to avoid opening unnecessary boxes,
However it seems like its not producing the expected results. The main contribution to that is unfortunate luck.
It appears that consistently for around 10-20 of the 100 trials, no cake spawns in any of the 8 boxes, so although
the final ratio is typically less that 1 cake : 4 boxes (the expected result), the results are still better than when 
I tested having the robot go over all 8 boxes in every trial. That strategy resulted an average of 0.15 each time.

With this in mind, my strategy was typically a little above 0.20, meaning my strategy of aborting after finding the
first cake performed slightly better that the strategy of checking every box. 
"""
