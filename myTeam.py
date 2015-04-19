# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'Agent540', second = 'Agent540'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class Agent540(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def initialize(self, gameState):
    "Initializes beliefs to a uniform distribution over all positions."
    # The legal positions do not include the ghost prison cells in the bottom left.
    self.legalPositions = [p for p in gameState.getWalls().asList(False) if p[1] > 1]

    #Get positions of walls. T/F List
    self.walls = list(gameState.getWalls())

  def initializeBeliefs(self, gameState):

    global beliefs
    #beliefs = [util.Counter()] * (gameState.getNumAgents())
    beliefs = [util.Counter()] * len(self.getOpponents(gameState))

    for i, val in enumerate(beliefs):
      if i in self.getOpponents(gameState):
          beliefs[i][gameState.getInitialAgentPosition(i)] = 1.0
    for i, belief in enumerate(beliefs):
      belief.normalize()

    #print beliefs

  def initializeHoverZones(self, gameState):
    if self.isRed:
      offset = -2
    else:
      offset = 3
    xPos = (self.width/2) + offset
    for i in range(self.height):
      if not self.walls[xPos][i]:
        self.hoverZones.append((xPos, i))

  def getMazeDimensions(self, gameState):
    self.wallPositions = gameState.getWalls().asList()
    self.width, self.height = self.wallPositions[len(self.wallPositions)-1]

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''
    self.initialize(gameState)
    self.initializeBeliefs(gameState)
    self.isRed = self.red

    #Get width and height of maze
    self.getMazeDimensions(gameState)

    #print self.legalPositions , "Legal"
    #print self.walls, "Wall"

    '''
    HoverZones - Regions where our ghosts will hangout
    Basically a vertical band near the transition area

    '''
    self.hoverZones = []
    self.initializeHoverZones(gameState)

    #print "hoverZones ", self.hoverZones

    quarterHeight = len(self.hoverZones) / 4
    threeFourthsHeight = 3 * len(self.hoverZones) / 4
    if self.index < 2:
      x, y = self.hoverZones[quarterHeight]
    else:
      x, y = self.hoverZones[threeFourthsHeight]

    self.target = (x, y)


    #How many moves should our agent attack?
    self.moves = 0
    #Has the pacman just been killed?
    self.pacmanKill = False


  def elapseTime(self, gameState):
    """
    Update beliefs for a time step elapsing.

    """
    "*** YOUR CODE HERE ***"

    '''
    Things to do
      1) Check if our ghost has JUST eaten a pacman. If yes, start attack!
        Change the self.pacmanKill variable

    '''


  #Took this from baselineTeam class
  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)
    #Should we remove stop? Seems like a waste of a move
    actions.remove('Stop')

    '''
    You should change this in your own agent.
    '''
    #Get noisy distances of all 4 agents
    agentDistances = gameState.getAgentDistances()
    #Get active agent's current position
    myPosition = gameState.getAgentPosition(self.index)

    #Update position beliefs of opposing agents
    for agent in self.getOpponents(gameState):
      noisyDistance = agentDistances[agent]
      #emissionModel = busters.getObservationDistribution(noisyDistance)
      agentPosition = gameState.getAgentPosition(self.index)

      allPossible = util.Counter()
      for p in self.legalPositions:
          trueDistance = util.manhattanDistance(p, agentPosition)
          allPossible[p] += gameState.getDistanceProb(trueDistance, noisyDistance)

      allPossible.normalize()
      #beliefs = allPossible

      for p in self.legalPositions:
        beliefs[agent][p] = beliefs[agent][p] * allPossible[p]

      beliefs[agent].normalize()


    '''
    Max number of moves our agent will attack.
    1) What if all the food are beyond 60 moves?
       Risk of increasing the number of moves - May lose the food eaten till that point because of greediness
    2) What if the attacking agent, returning to our side, misses food on the way back because the 60 move limit has been reached?

    Or should we also incorporate another limit metric? The number of food eaten?
    1) If eaten 5 food, return.

    '''

    self.elapseTime(gameState)

    bestAction = ''
    bestActionUtility = -float("inf")

    #If a pacman has been killed, start attack and keep on attacking for a number of moves
    if self.pacmanKill and self.moves < 60:
      for action in actions:
        utility = self.Attack(gameState, action)
        if utility > bestActionUtility:
          bestAction = action
          bestActionUtility = utility
    else:
      self.pacmanKill = False
      self.moves = 0
      for action in actions:
        utility = self.Defend(gameState, action)
        if utility > bestActionUtility:
          bestAction = action
          bestActionUtility = utility

    return bestAction

    #return random.choice(actions)

    #End of chooseAction



  """
    Unecessary improvement ideas (Once everything is working)

    Create some form of lookahead mechanism while attacking?
    If a pacman has to return to its current position NO MATTER WHAT in the future, (i.e. going into a dead end more than 3 moves deep), maybe don't take that course of action?

  """


  #return utility of this new state
  def Attack(self, gameState, action):

    #Needs to keep track of how long our pacman has been attacking
    self.moves += 1



  #return utility of this new state
  def Defend(self, gameState, action):
    # not implemented
    a = 0
