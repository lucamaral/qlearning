# -*- coding: utf-8 -*-

# AUTOR: LUCAS AMARAL

import numpy as np
from tabulate import tabulate
from copy import deepcopy
import matplotlib.pyplot as plt
import gym
from gym import spaces
import time

RIGHT_ACTION = 0
DOWN_ACTION = 1
LEFT_ACTION = 2
UP_ACTION = 3
STAY_ACTION = 4
action_dict = {0:"RIGHT", 1:"DOWN", 2:"LEFT", 3:"UP", 4:"STAY"}

OBJ = b'O'
WALL = b'P'
BASE = b'B'
AGENT = b'1'

class Environment(gym.Env):
  
  metadata = {'render.modes': ['console']}

  def __init__(self, is_printing=True):
    super(Environment, self).__init__()
    self.is_printing = is_printing


    # Tamanho do mundo grid
    self.rows = 6
    self.cols = 7
    
    # Posição inicial do agente
    self.start_agent_pos = (5,0)
    self.cur_agent_pos = self.start_agent_pos
    
    # Posição inicial do objeto
    self.start_obj_pos = (2, 3)
    self.cur_obj_pos = self.start_obj_pos
    
    # Criação do grid representante as paredes/bases/posicao do agente/posicao do objeto
    self.create_grid()
    
    # Criação dos espaços
    n_actions = 4
    self.action_space = spaces.Discrete(n_actions)
    self.observation_space = spaces.Discrete(self.rows * self.cols)
    
    # Indicador se o objeto está sendo segurado
    self.obj_captured = False
    
  def observation(self, state):
      return state[0] * self.cols + state[1]

  def create_grid(self):
    self.grid = np.chararray((self.rows, self.cols))
    self.grid[:] = '-'
    self.grid[0, 2:5] = BASE
    self.grid[1, 3] = WALL
    self.grid[4, 0:2] = WALL
    self.grid[4, 3:7] = WALL
    self.grid[self.cur_obj_pos[0], self.cur_obj_pos[1]] = OBJ
    self.grid[self.cur_agent_pos[0], self.cur_agent_pos[1]] = AGENT

  def reset(self):
    self.cur_agent_pos = self.start_agent_pos
    self.cur_obj_pos = self.start_obj_pos
    self.obj_captured = False
    return self.observation(self.cur_agent_pos)  
  
  def step(self, action):
    # Reward de -1 pela ação executada
    reward = -1.0

    # Variável indicando se o agente terminou a caminhada
    done = False

    next_agent_pos = list(deepcopy(self.cur_agent_pos))
    agent_row = next_agent_pos[0]
    agent_col = next_agent_pos[1]

    next_obj_pos = list(deepcopy(self.cur_obj_pos))
    obj_row = next_obj_pos[0]
    obj_col = next_obj_pos[1]

    new_agent_row, new_agent_col = self.calculate_new_pos(agent_row, agent_col, action)
    new_obj_row, new_obj_col = self.calculate_new_pos(obj_row, obj_col, action)

    agent_moved = False
    obj_moved = False

    # Verifica se é possível mover o agente
    agent_moved = self.can_move_agent(new_agent_row, new_agent_col)

    # Caso seja possível mover o agente
    if agent_moved:
        # Caso o agente já esteja segurando o objeto
        if self.obj_captured:
            # Verifica se é possível mover o objeto
            obj_moved = self.can_move_obj(new_obj_row, new_obj_col)

            # O agente só move se o objeto mover também
            agent_moved = agent_moved and obj_moved

            # Caso o objeto pode ser movido também
            if obj_moved:
                # Atualizar posições do agente
                next_agent_pos[0] = new_agent_row
                next_agent_pos[1] = new_agent_col

                # Atualizar posições do objeto
                next_obj_pos[0] = new_obj_row
                next_obj_pos[1] = new_obj_col
        else:
            # Atualizar posições do agente
            next_agent_pos[0] = new_agent_row
            next_agent_pos[1] = new_agent_col

    if agent_moved is False:
        reward = -5

    self.cur_agent_pos = tuple(next_agent_pos)
    self.cur_obj_pos = tuple(next_obj_pos)

    agent_row = self.cur_agent_pos[0]
    agent_col = self.cur_agent_pos[1]

    # Verificar se o agente está do lado do objeto
    if self.obj_captured is False and agent_row == 2 and agent_col in [2,4]:
        self.obj_captured = True

    # Verifica se o agente chegou na base com/sem o objeto
    if self.grid[agent_row, agent_col] == BASE:
        # Reward de -100 por ter chegado na base sem o objeto
        reward = 1 if self.obj_captured else -100
        done = self.obj_captured
        if self.obj_captured is False:
            self.cur_agent_pos = self.start_agent_pos

    obj_row = self.cur_obj_pos[0]
    obj_col = self.cur_obj_pos[1]

    # Verifica se o objeto chegou na base
    if self.grid[obj_row, obj_col] == BASE:
        reward = 1 if self.obj_captured else reward
        done = True

    return self.observation(self.cur_agent_pos), reward, done, {}

  def calculate_new_pos(self, pos_row, pos_col, action):
    if action == RIGHT_ACTION:
        return pos_row, pos_col + 1
    if action == LEFT_ACTION:
        return pos_row, pos_col - 1
    if action == DOWN_ACTION:
        return pos_row + 1, pos_col
    if action == UP_ACTION:
        return pos_row - 1, pos_col
    return pos_row, pos_col

  def can_move_agent(self, row, col):
    # Fora dos limites ou movendo para parede
    if self.out_of_limits_or_walls(row, col):
      return False

    # Mover para casa do objeto, 
    if self.grid[row, col] == OBJ:

      # Verifica se o objeto já foi capturado
      if self.obj_captured:
          
          # Caso a posição da coluna já está no limite
          if col == 0 or col == self.cols - 1:
              return False

          # Caso a posição da linha já está no limite
          if row == 0 or row == self.rows - 1:
              return False
      else:
          # Sem ter capturado o objeto antes
          return False

    return True

  def can_move_obj(self, row, col):
    # Fora dos limites ou movendo para parede
    return self.out_of_limits_or_walls(row, col) is False  

  def out_of_limits_or_walls(self, row, col):
    # Fora dos limites
    if row < 0 or col < 0 or row >= self.rows or col >= self.cols:
        return True

    # Mover para paredes
    if self.grid[row, col] == WALL:
        return True
    return False

  def render(self):
    self.create_grid()
    if self.is_printing:
        print(tabulate(self.grid, tablefmt="fancy_grid"))

def Qlearning(environment, num_episodes=100, alpha=0.3, gamma=0.9, epsilon=1.0, decay_epsilon=0.1, max_epsilon=1.0, min_epsilon=0.01):
  
  # initializing the Q-table
  Q = np.zeros((environment.observation_space.n, environment.action_space.n))

  # additional lists to keep track of reward and epsilon values
  rewards = []
  epsilons = []

  # episodes
  for episode in range(num_episodes):
      
      # reset the environment to start a new episode
      state = environment.reset()

      # reward accumulated along episode
      accumulated_reward = 0

      # steps within current episode
      for step in range(100):
          
          # epsilon-greedy action selection
          # exploit with probability 1-epsilon
          if np.random.uniform(0, 1) > epsilon:
              action = np.argmax(Q[state,:])
                # explore with probability epsilon
          else:
              action = environment.action_space.sample()

          if environment.is_printing and episode % 10 == 0:
            print(f"Episode {episode} | Step {step} | Action {action_dict[action]}")

          # perform the action and observe the new state and corresponding reward
          new_state, reward, done, info = environment.step(action)

          # update the Q-table
          Q[state, action] = Q[state, action] + alpha * (reward + gamma * np.max(Q[new_state, :]) - Q[state, action])
          
          # update the accumulated reward
          accumulated_reward += reward

          # update the current state
          state = new_state

          # render the environment
          environment.render()
          
          # end the episode when it is done
          if done == True:
              break

      # decay exploration rate to ensure that the agent exploits more as it becomes experienced
      epsilon = min_epsilon + (max_epsilon - min_epsilon)*np.exp(-decay_epsilon*episode)
      
      # update the lists of rewards and epsilons
      rewards.append(accumulated_reward)
      epsilons.append(epsilon)

  # render the environment
  environment.render()
    
  # return the list of accumulated reward along episodes
  return rewards

num_episodes=200
alpha=0.3
gamma=0.9
epsilon=1
decay_epsilon=0.3
max_epsilon=1
min_epsilon=0.001

# run Q-learning
is_printing=False
env = Environment(is_printing)
print("Estado inicial")
env.render()
start = time.time()
rewards = Qlearning(env, num_episodes, alpha, gamma, epsilon, decay_epsilon, max_epsilon, min_epsilon)
end = time.time()
print(f"Execution time {end - start}")

# print results
print ("Average reward (all episodes): " + str(sum(rewards)/num_episodes))
print ("Average reward (last 10 episodes): " + str(sum(rewards[-10:])/10))

plt.plot(range(num_episodes), rewards)
plt.xlabel('Episodes')
plt.ylabel('Accumulated reward along episodes')
plt.show()