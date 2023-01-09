from rlcard.utils import *
import pdb
import pickle
import time
import random
import copy
import gc
import numpy as np
import multiprocessing as mp

class Env(object):
    '''
    The base Env class. For all the environments in RLCard,
    we should base on this class and implement as many functions
    as we can.
    '''
    def __init__(self, config):
        ''' Initialize the environment

        Args:
            config (dict): A config dictionary. All the fields are
                optional. Currently, the dictionary includes:
                'seed' (int) - A environment local random seed.
                'allow_step_back' (boolean) - True if allowing
                 step_back.
                There can be some game specific configurations, e.g., the
                number of players in the game. These fields should start with
                'game_', e.g., 'game_num_players' which specify the number of players in the game. Since these configurations may be game-specific,
                The default settings should be put in the Env class. For example,
                the default game configurations for Blackjack should be in
                'rlcard/envs/blackjack.py'
                TODO: Support more game configurations in the future.
        '''
        self.allow_step_back = self.game.allow_step_back = config['allow_step_back']
        self.action_recorder = []

        # Game specific configurations
        # Currently only support blackjack、limit-holdem、no-limit-holdem
        # TODO support game configurations for all the games
        supported_envs = ['blackjack', 'leduc-holdem', 'limit-holdem', 'no-limit-holdem']
        if self.name in supported_envs:
            _game_config = self.default_game_config.copy()
            for key in config:
                if key in _game_config:
                    _game_config[key] = config[key]
            self.game.configure(_game_config)

        # Get the number of players/actions in this game
        self.num_players = self.game.get_num_players()
        self.num_actions = self.game.get_num_actions()

        # A counter for the timesteps
        self.timestep = 0

        # Set random seed, default is None
        self.seed(config['seed'])

    def reset(self):
        ''' Start a new game

        Returns:
            (tuple): Tuple containing:

                (numpy.array): The begining state of the game
                (int): The begining player
        '''
        state, player_id = self.game.init_game()
        self.action_recorder = []
        state0 = self._extract_state(state[0])
        state1 = self._extract_state(state[1])
        return [state0, state1], player_id

    def step(self, action, raw_action=False):
        ''' Step forward

        Args:
            action (int): The action taken by the current player
            raw_action (boolean): True if the action is a raw action

        Returns:
            (tuple): Tuple containing:

                (dict): The next state
                (int): The ID of the next player
        '''
        if not raw_action:
            action = self._decode_action(action)
        action0, action1 = action

        self.timestep += 1
        # Record the action for human interface
        self.action_recorder.append([(0, action0), (1, action1)])
        a = time.time()
        next_state, player_id = self.game.step(action)
        b = time.time()
        #print(b-a)
        state = [self._extract_state(next_state[0]), self._extract_state(next_state[1])]

        return state, player_id

    def step_back(self):
        ''' Take one step backward.

        Returns:
            (tuple): Tuple containing:

                (dict): The previous state
                (int): The ID of the previous player

        Note: Error will be raised if step back from the root node.
        '''
        if not self.allow_step_back:
            raise Exception('Step back is off. To use step_back, please set allow_step_back=True in rlcard.make')

        if not self.game.step_back():
            return False

        player_id = self.get_player_id()
        state = self.get_state(player_id)

        return state, player_id

    def set_agents(self, agents):
        '''
        Set the agents that will interact with the environment.
        This function must be called before `run`.

        Args:
            agents (list): List of Agent classes
        '''
        self.agents = agents

    def run(self, is_training=False):
        '''
        Run a complete game, either for evaluation or training RL agent.

        Args:
            is_training (boolean): True if for training purpose.

        Returns:
            (tuple) Tuple containing:

                (list): A list of trajectories generated from the environment.
                (list): A list payoffs. Each entry corresponds to one player.

        Note: The trajectories are 3-dimension list. The first dimension is for different players.
              The second dimenion is for different transitions. The third dimension is for the contents of each transiton
        '''
        trajectories = [[] for _ in range(self.num_players)]
        state, player_id = self.reset()

        # Loop to play the game
        for i in range(self.num_players):
            trajectories[player_id[i]].append(state[player_id[i]])
        while not self.is_over():
            # Agent plays
            if not is_training:
                action0, _ = self.agents[0].eval_step(state[0])
                action1, _ = self.agents[1].eval_step(state[1])
            else:
                action0 = self.agents[0].step(state[0])
                action1 = self.agents[1].step(state[1])
            act0 = state[0]['raw_obs']['actionsIdx'][action0]
            act1 = state[1]['raw_obs']['actionsIdx'][action1]
            action = [act0, act1]

            # Environment steps
            next_state, next_player_id = self.step(action, True)
            # Save action
            act0 = state[0]['raw_obs']['actions'][action0]
            act1 = state[1]['raw_obs']['actions'][action1]
            action = [act0, act1]
            trajectories[0].append(act0)
            trajectories[1].append(act1)

            # Save state.
            if not self.game.is_over():
                trajectories[0].append(state[0])
                trajectories[1].append(state[1])

            # Set the state and player
            state = next_state
            player_id = next_player_id

        # Add a final state to all the players
        for player_id in range(self.num_players):
            trajectories[player_id].append(state[player_id])
            trajectories[player_id].append([[], [], []])

        # Payoffs
        payoffs = self.get_payoffs()

        return trajectories, payoffs


    def runLoop(self, agent, nums, pid, data_path, gpu_idx, training=True):
        countGame = 0
        count_data = 0
        self.set_agents(agent)
        try:
            with open(data_path + 'gpu' + str(gpu_idx) + '/data'+str(pid)+'.pickle', 'rb') as f:
                pass
        except:
            with open(data_path + 'gpu' + str(gpu_idx) + '/data'+str(pid)+'.pickle', 'wb') as f:
                pickle.dump(0, f)
        while True:
            countGame += 1
            state, player_id = self.reset()
            cntAct = 0
            # Loop to play the game
            while not self.is_over():
                trajectoriesRound = [[] for _ in range(self.num_players)]
                actPayoffs = [[] for _ in range(self.num_players)]
                curPvp = self.game.copy_game(self.game.pvp)
                curStateObs = [state[i]['obs'] for i in range(self.num_players)]
                curRoundNum = self.game.pvp.rnd.roundNum
                # Agent plays
                for i in range(self.num_players):
                    length = len(state[i]['legal_actions'])
                    nums = round(nums+0.001) if nums<50 else 50
                    for actIdx in range(length):
                        aaa = time.time()
                        payoffsTmp = 0
                        thisRnd = 0
                        for _ in range(nums):
                            self.game.pvp = self.game.copy_game(curPvp)
                            stateTmp = state
                            flag = 1
                            while not self.is_over():
                                eIdx = 0 if i else 1
                                if not training:
                                    eAction, _ = self.agents[eIdx].eval_step(stateTmp[eIdx])
                                else:
                                    eAction = self.agents[eIdx].step(stateTmp[eIdx])
                                eAct = stateTmp[eIdx]['raw_obs']['actionsIdx'][eAction]
                                if flag:
                                    actIdxTmp = stateTmp[i]['raw_obs']['actionsIdx'][actIdx]
                                    flag = 0
                                else:
                                    if not training:
                                        actIdxTmp, _ = self.agents[i].eval_step(stateTmp[i])
                                    else:
                                        actIdxTmp = self.agents[i].step(stateTmp[i])
                                    actIdxTmp = stateTmp[i]['raw_obs']['actionsIdx'][actIdxTmp]
                                action = [eAct, actIdxTmp] if i == 1 else [actIdxTmp, eAct]
                                stateTmp, _ = self.step(action, True)
                            exp = self.game.pvp.rnd.roundNum-curRoundNum
                            discount = 0.95**exp
                            payoffsTmp += discount * self.get_payoffs()[i]
                        payoffsTmp = round(payoffsTmp/nums, 3)
                        actPayoffs[i].append(payoffsTmp)
                        raw_act = state[i]['raw_obs']['actions'][actIdx]
                        aClass = ['reptile', 'plant', 'dusk',
                                  'aquatic', 'bird', 'dawn',
                                  'beast', 'bug', 'mech']
                        attackType = ['melee', 'ranged', 'support']
                        part = ['mouth', 'horn', 'back', 'tail']
                        info = []
                        for acts in raw_act:
                            tmp = []
                            for j in range(4):
                                if len(acts) >= j+1:
                                    card = acts[j]
                                    tmp = [card.idx, aClass.index(card.cProp),
                                           card.cost, card.attack, card.defend,
                                           attackType.index(card.attackType),
                                           part.index(card.bodyPart)]
                                else:
                                    tmp = [-1]*7
                                info.extend(tmp)
                        stateObsTmp = copy.deepcopy(curStateObs[i].tolist())
                        stateObsTmp.extend(info)
                        data = np.hstack((stateObsTmp, payoffsTmp))
                        # 载入数据
                        with open(data_path+'gpu'+str(gpu_idx)+'/data'+str(pid)+'.pickle', 'rb') as f:
                            total_data = pickle.load(f)
                        with open(data_path+'gpu'+str(gpu_idx)+'/data'+str(pid)+'.pickle', 'wb') as f:
                            if type(total_data) == int:
                                pickle.dump(data, f)
                                count_data = 1
                            else:
                                total_data = np.vstack((total_data, data))
                                pickle.dump(total_data, f)
                                count_data += 1
                        with open(data_path+'gpu'+str(gpu_idx)+'/count'+str(pid)+'.pickle', 'wb') as f:
                            pickle.dump(count_data, f)
                        bbb = time.time()
                        print(pid, count_data, round((bbb-aaa)*10)/10, 's  --------------------')

                        stateObsTmp.append(payoffsTmp)
                        trajectoriesRound[i].append(stateObsTmp)
                        cntAct += 1

                trajectoriesRound = [np.asarray(trajectoriesRound[0]),
                                     np.asarray(trajectoriesRound[1])]
                action0 = self.choice(trajectoriesRound[0][:, -1])
                action1 = self.choice(trajectoriesRound[1][:, -1])
                act0 = state[0]['raw_obs']['actionsIdx'][action0]
                act1 = state[1]['raw_obs']['actionsIdx'][action1]
                action = [act0, act1]

                # Environment steps
                self.game.pvp = self.game.copy_game(curPvp)
                next_state, _ = self.step(action, True)

                # Set the state and player
                state = next_state
                trajectoriesRound = np.vstack((trajectoriesRound[0], trajectoriesRound[1]))
            
                print(i, countGame, curRoundNum)
                gc.collect()

            # 载入本局最后两个数据
            stateObs0 = state[0]['obs'].tolist()
            stateObs0.extend([-1]*84)
            stateObs0.append(self.get_payoffs()[0])
            stateObs1 = state[1]['obs'].tolist()
            stateObs1.extend([-1]*84)
            stateObs1.append(self.get_payoffs()[1])
            data = np.asarray(stateObs0)
            with open(data_path + 'gpu' + str(gpu_idx) + '/data'+str(pid)+'.pickle', 'rb') as f:
                total_data = pickle.load(f)
            with open(data_path + 'gpu' + str(gpu_idx) + '/data'+str(pid)+'.pickle', 'wb') as f:
                if type(total_data) == int:
                    pickle.dump(data, f)
                    count_data = 1
                else:
                    total_data = np.vstack((total_data, data))
                    pickle.dump(total_data, f)
                    count_data += 1
            with open(data_path + 'gpu' + str(gpu_idx) + '/count'+str(pid)+'.pickle', 'wb') as f:
                pickle.dump(count_data, f)
            data = np.asarray(stateObs1)
            with open(data_path + 'gpu' + str(gpu_idx) + '/data'+str(pid)+'.pickle', 'rb') as f:
                total_data = pickle.load(f)
            with open(data_path + 'gpu' + str(gpu_idx) + '/data'+str(pid)+'.pickle', 'wb') as f:
                if type(total_data) == int:
                    pickle.dump(data, f)
                    count_data = 1
                else:
                    total_data = np.vstack((total_data, data))
                    pickle.dump(total_data, f)
                    count_data += 1
            with open(data_path + 'gpu' + str(gpu_idx) + '/count'+str(pid)+'.pickle', 'wb') as f:
                pickle.dump(count_data, f)

    def softmax(self, trajectories):
        exp = np.exp(trajectories)
        sumExp = np.sum(exp)
        return np.round(exp/sumExp, 3)

    def choice(self, trajectories):
        maximum = np.max(trajectories)
        return random.choice(np.where(trajectories == maximum)[0])

    def is_over(self):
        ''' Check whether the curent game is over

        Returns:
            (boolean): True if current game is over
        '''
        return self.game.is_over()

    def get_player_id(self):
        ''' Get the current player id

        Returns:
            (int): The id of the current player
        '''
        return [0, 1]


    def get_state(self, player_id):
        ''' Get the state given player id

        Args:
            player_id (int): The player id

        Returns:
            (numpy.array): The observed state of the player
        '''
        return self._extract_state(self.game.get_state(player_id))

    def get_payoffs(self):
        ''' Get the payoffs of players. Must be implemented in the child class.

        Returns:
            (list): A list of payoffs for each player.

        Note: Must be implemented in the child class.
        '''
        raise NotImplementedError

    def get_perfect_information(self):
        ''' Get the perfect information of the current state

        Returns:
            (dict): A dictionary of all the perfect information of the current state
        '''
        raise NotImplementedError

    def get_action_feature(self, action):
        ''' For some environments such as DouDizhu, we can have action features

        Returns:
            (numpy.array): The action features
        '''
        # By default we use one-hot encoding
        feature = np.zeros(self.num_actions, dtype=np.int8)
        idx = self.game.actions_data.index(action)
        feature[idx] = 1
        return feature

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        self.game.np_random = self.np_random
        return seed

    def _extract_state(self, state):
        ''' Extract useful information from state for RL. Must be implemented in the child class.

        Args:
            state (dict): The raw state

        Returns:
            (numpy.array): The extracted state
        '''
        raise NotImplementedError

    def _decode_action(self, action_id):
        ''' Decode Action id to the action in the game.

        Args:
            action_id (int): The id of the action

        Returns:
            (string): The action that will be passed to the game engine.

        Note: Must be implemented in the child class.
        '''
        raise NotImplementedError

    def _get_legal_actions(self):
        ''' Get all legal actions for current state.

        Returns:
            (list): A list of legal actions' id.

        Note: Must be implemented in the child class.
        '''
        raise NotImplementedError
