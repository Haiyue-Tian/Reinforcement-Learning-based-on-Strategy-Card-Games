import argparse
import importlib
import time
import pdb
import random
import numpy as np
import tf_slim as slim
from rlcard.agents.mobileNet_agents import data
from rlcard.agents.mobileNet_agents import tfrecorder
from rlcard.agents.mobileNet_agents.parameters import parameters2_1 as pm
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()


class MobileNetAgent(object):
    ''' A random agent. Random agents is for running toy examples on the card games
    '''

    def __init__(self, state_shape,
                 action_shape,
                 sys,
                 is_train=False,
                 memory_size=20000,
                 batch_size=128,
                 replace_target_iter=200,
                 epsilon_increment=None,
                 epsilon_max=0.9):
        ''' Initilize the random agent

        Args:
            num_actions (int): The size of the ouput action space
        '''
        self.replace_target_iter = replace_target_iter
        self.name = 'mobileNetAgent'
        self.epsilon_max = epsilon_max
        self.epsilon_increment = epsilon_increment
        self.epsilon = 0 if self.epsilon_increment is not None else self.epsilon_max
        self.global_step = tf.Variable(0, trainable=False, name='global_step')
        self.step_counter = 0
        self.use_raw = False
        self.is_train = is_train
        self.state_shape = state_shape
        self.action_shape = action_shape
        self.args = pm.parse_arguments(sys)
        self.label = tf.placeholder(tf.float32, self.args.batch_size)
        self.memory_size = memory_size
        self.batch_size = batch_size
        self.network = importlib.import_module(self.args.model)
        self.inputData = tf.placeholder(tf.float32, shape=(551))
        self.qInputData = tf.placeholder(tf.float32, shape=(self.args.batch_size, 551))
        self.q_estimator = self.network.inference(self.qInputData,
                                                  self.args.model_def,
                                                  self.args.test_phase_train,
                                                  'q_estimator_')
        self.target_estimator = self.network.inference(self.inputData,
                                                       self.args.model_def,
                                                       self.args.test_phase_train,
                                                       'target_estimator_')
        self.q_est = tf.reshape(self.q_estimator, (self.args.batch_size,))
        self.total_loss = data.loss(self.q_est, self.label)
        self.optimizer =data.training(self.args.optimizer, self.args.learning_rate_parameters, self.global_step)
        self.train_op = self.optimizer.minimize(self.total_loss, global_step=self.global_step)

        t_params = slim.get_variables_to_restore(include=["target_estimator"])
        q_params = slim.get_variables_to_restore(include=["q_estimator"])

        q_params_to_restore=[]
        for var in q_params:
            q_params_to_restore.append(var)

        model_name = "q_estimator_"
        checkpoint_model_scope = ""
        q_params_to_restore = {var.op.name.replace(model_name,
                               checkpoint_model_scope): var
                               for var in q_params_to_restore}
        target_params_to_restore = []
        for var in t_params:
            target_params_to_restore.append(var)

        model_name = "target_estimator_"
        checkpoint_model_scope = ""
        target_params_to_restore = {var.op.name.replace(model_name,
                                    checkpoint_model_scope): var
                                    for var in target_params_to_restore}
        self.replace_target_op = [tf.assign(t, q) for t, q in zip(t_params, q_params)]

        if is_train:
            self.sess = tf.Session()
            self.sess.run(tf.global_variables_initializer())
            saver = tf.train.Saver(target_params_to_restore)
            print('Reading Checkpoint...')
            ckpt = tf.train.get_checkpoint_state(self.args.train_model_dir)
            print(ckpt.model_checkpoint_path)
            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(self.sess, ckpt.model_checkpoint_path)
                global_step = ckpt.model_checkpoint_path.split('/')[-1].split('-')[-1]
                print('Loading success, global step is %s' % global_step)
            else:
                print('No checkpoint file found')
            self.cost_his = []
        else:
            self.sess = tf.Session()
            self.sess.run(tf.local_variables_initializer())
            saver = tf.train.Saver(target_params_to_restore)
            print('Reading Checkpoint...')
            ckpt = tf.train.get_checkpoint_state(self.args.train_model_dir)
            print(ckpt.model_checkpoint_path)
            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(self.sess, ckpt.model_checkpoint_path)
                global_step = ckpt.model_checkpoint_path.split('/')[-1].split('-')[-1]
                print('Loading success, global step is %s' % global_step)
            else:
                print('No checkpoint file found')

    def predict(self, state):
        legal_actions = state['legal_actions']
        action_keys = np.array(list(legal_actions.keys()))
        action_values = list(legal_actions.values())
        # One-hot encoding if there is no action features
        for i in range(len(action_values)):
            if action_values[i] is None:
                action_values[i] = np.zeros(self.action_shape[0])
                raw_act = state['raw_obs']['actions'][action_keys[i]]
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
                action_values[i] = info
        action_values = np.array(action_values, dtype=np.float32)

        q_values = np.zeros(len(action_values))
        for i in range(len(action_values)):
            s = np.hstack((state['obs'], action_values[i]))
            s.reshape((551))
            q_values[i] = self.sess.run(self.target_estimator, feed_dict={self.inputData: s})
        masked_q_values = -np.inf * np.ones(len(action_values), dtype=float)
        legal_actions = list(state['legal_actions'].keys())
        masked_q_values[legal_actions] = q_values[legal_actions]
        return masked_q_values

    def step(self, state):
        ''' Predict the action given the curent state in gerenerating training data.

        Args:
            state (dict): An dictionary that represents the current state

        Returns:
            action (int): The action predicted (randomly chosen) by the random agent
        '''
        q_values = self.predict(state)
        if random.random() < self.epsilon:
            best_action = np.argmax(q_values)
        else:
            candi = [i for i in range(q_values.shape[0])]
            best_action = np.random.choice(candi)
        return best_action

    def eval_step(self, state):
        ''' Predict the action given the current state for evaluation.
            Since the random agents are not trained. This function is equivalent to step function

        Args:
            state (dict): An dictionary that represents the current state

        Returns:
            action (int): The action predicted (randomly chosen) by the random agent
            probs (list): The list of action probabilities
        '''

        q_values = self.predict(state)
        best_action = np.argmax(q_values)

        info = {}
        return best_action, info

    def store_transition(self, state, q_value, manager, lock):
        lock.aquire()
        transition = np.hstack((state, q_value))
        index = manager['memory_counter'] % self.memory_size
        manager['memory'][index, :] = transition
        manager['memory_counter'] += 1
        lock.release()

    def learn(self, manager, lock):
        # if self.step_counter % self.replace_target_iter == 0:
        #     self.sess.run(self.replace_target_op)
        #     print('\ntarget_params_replaced\n')
        if manager['memory_counter'] != manager['lastCount']:
            print(manager['memory_counter'], end=' ')
            manager['lastCount'] = manager['memory_counter']

        # if manager['memory_counter'] > self.memory_size:
        #     sample_index = np.random.choice(self.memory_size,
        #                                     size=self.batch_size)
        # else:
        #     sample_index = np.random.choice(manager['memory_counter'],
        #                                     size=self.batch_size)
        # batch_memory = manager['memory'][sample_index, :]
        #
        # _, batch_loss = self.sess.run([self.train_op, self.total_loss], feed_dict={
        #                                self.qInputData: batch_memory[:, :-1],
        #                                self.label: batch_memory[:, -1]})
        # self.cost_his.append(batch_loss)
        #
        # self.epsilon = self.epsilon + self.epsilon_increment if self.epsilon < self.epsilon_max else self.epsilon_max
        # if self.step_counter % 100 == 0:
        #     print('step: ', self.step_counter, ' loss: ', batch_loss)
        # self.step_counter += 1
