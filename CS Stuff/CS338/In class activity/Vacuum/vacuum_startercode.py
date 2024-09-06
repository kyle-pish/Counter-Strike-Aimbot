# code written by Andrew Shallue, CS338, Spring 2023
# code for a simple vacuum cleaning agent

import random as rand


# this environment is deterministic
class Environment1:

  def __init__(self):
    self.boxes = []

    # fill boxes with dirt at probabilty 1/4
    for i in range(4):
      pull = rand.randint(0, 4)
      if pull == 0:
        self.boxes.append("dirt")
      else:
        self.boxes.append("nothing")


# this environment is stochastic - we update dirt at each time step
class Environment2:

  def __init__(self):
    self.boxes = []

    # fill boxes with dirt at probabilty 1/4
    for i in range(4):
      pull = rand.randint(0, 4)
      if pull == 0:
        self.boxes.append("dirt")
      else:
        self.boxes.append("nothing")

  def update(self):
    # loop over all the boxes.  If it contains nothing, add dirt with probability 1/10
    for i in range(len(self.boxes)):
      entry = self.boxes[i]
      if entry == "nothing":
        pull = rand.randint(0, 10)
        if pull == 0:
          self.boxes[i] = "dirt"


class Agent:

  def __init__(self):
    self.pos = 0
    self.dirt_cleaned = 0
    self.num_moves = 0
    self.azeem = 0
    
  
    
  def leftright(self, direction, env):
      """Moves the agent left or right if possible."""
      if direction == 'left':
          if self.pos > 0:
              self.pos -= 1
              self.num_moves += 1
      elif direction == 'right':
          if self.pos < len(env.boxes) - 1:
              self.pos += 1
              self.num_moves += 1   

  def get_percept(self, env):
      """Returns the percept of the current square: 'dirt' or 'nothing'."""
      return env.boxes[self.pos]
  

  def clean_strategy_env1(self, env):
        """
        Cleaning deterministic environment
        """
        while 'dirt' in env.boxes:
            if self.get_percept(env) == 'dirt':
                self.dirt_cleaned += 1
                env.boxes[self.pos] = 'nothing'  # Clean the dirt
            # Move to the right until the end, then to the left
            if self.pos < len(env.boxes) - 1:
                self.leftright('right', env)
            else:
                self.leftright('left', env)
        # Calculate the performance measure
        score = 4 * self.dirt_cleaned / self.num_moves if self.num_moves > 0 else 0
        return score
  
  def clean_strategy_env2(self, env):
        """
        Cleaning stochastic environment
        """
        for _ in range(100):  # Simulate 100 moves
            
            # Print the environment and agent's current position before each action
            print(f"Environment: {env.boxes}, Agent Position: {self.pos}")

            # Check if the current position has dirt
            if self.get_percept(env) == 'dirt':
                print(f"Cleaning dirt at position {self.pos}.")
                self.dirt_cleaned += 1
                env.boxes[self.pos] = 'nothing'  # Clean the dirt

            env.update()  # Update the environment
            
            # Randomly decide to move left or right to find more dirt
            if rand.choice([True, False]):
                self.leftright('right', env)
            else:
                self.leftright('left', env)
        
        # Print the final state of the environment and agent's position
        print(f"Final Environment: {env.boxes}, Final Agent Position: {self.pos}")
        
        # Calculate the performance measure
        score = 4 * self.dirt_cleaned / self.num_moves if self.num_moves > 0 else 0
        return score


def main():
    num_trials = 100  # Number of trials
    total_score_env1 = 0
    total_score_env2 = 0

    for i in range(num_trials):
        
        print("")
        print("Trial: ", i)
        print("")

        """
        # Environment 1 Trial
        print("Environment 1")
        E1 = Environment1()
        agent1 = Agent()
        score1 = agent1.clean_strategy_env1(E1)
        total_score_env1 += score1
        """
        
        print("Environment 2")
        # Environment 2 Trial
        E2 = Environment2()
        agent2 = Agent()
        score2 = agent2.clean_strategy_env2(E2)
        total_score_env2 += score2

    # Calculate average scores
    avg_score_env1 = total_score_env1 / num_trials
    avg_score_env2 = total_score_env2 / num_trials

    print(f"Average agent score in Environment 1 after {num_trials} trials: {avg_score_env1:.2f}")
    print(f"Average agent score in Environment 2 after {num_trials} trials: {avg_score_env2:.2f}")

if __name__ == '__main__':
    main()

'''
def main():

  E = Environment2()

  for i in range(20):
    print(E.boxes)
    E.update()

    a = Agent()
    a.get_percept(E)
    a.pos = a.pos + 1
    print (a.get_percept(E))

if __name__ == '__main__':
  main()
'''
  
