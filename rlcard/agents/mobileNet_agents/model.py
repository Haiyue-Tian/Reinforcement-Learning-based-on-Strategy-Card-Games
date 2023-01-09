# Copyright 2021 RLCard Team of Texas A&M University
# Copyright 2021 DouZero Team of Kwai
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import pdb
import psutil
import time
import copy
import pickle
import random
import torch
import numpy as np
from torch import nn
from rlcard.agents.mobileNet_agents.models import mobileNetV3 as mbnet
from rlcard.agents.mobileNet_agents.models import fcModel
from torch.utils.tensorboard import SummaryWriter
from torch.nn.parallel import DataParallel
import traceback

class DMCAgent:
    def __init__(self,
                 state_shape,
                 action_shape,
                 exp_epsilon=0.01,
                 epsilon_max=0.9999,
                 epsilon_increment=0.001,
                 load_model=None,
                 max_split_size=2048,
                 log_path = None,
                 device_ids=[0]):
        self.use_raw = False
        self.log_path = log_path # model saved in this file
        self.epsilon_max = epsilon_max
        self.epsilon_increment = epsilon_increment
        self.epsilon = self.epsilon_max
        self.device_ids = device_ids
        self.device = torch.device('cuda:'+str(device_ids[0]) if device_ids[0]>=0 else 'cpu') 
        # self.net = mbnet.MobileNetV3().to(self.device).share_memory()
        self.net = fcModel.fcModel().to(self.device).share_memory()
        # self.net = DataParallel(self.net, device_ids=self.device_ids, output_device=self.device)
        self.load_model = load_model
        try:
            with open(self.log_path + 'model_path.txt') as f:
                model_name = f.readlines()[0]
            self.model_name = model_name
            self.net.load_state_dict(torch.load(self.log_path+model_name))
            print('load '+self.model_name+' success')
        except:
            pass
        if self.load_model is not None:
            self.net.load_state_dict(torch.load(self.load_model))
        self.exp_epsilon = exp_epsilon
        self.action_shape = action_shape
        self.state_shape = state_shape
        self.loss = nn.MSELoss(reduction='mean')
        self.optim = torch.optim.Adam(self.net.parameters())
        self.max_split_size = max_split_size
        self.model_name = None
        
    def step(self, state):
        # 加载模型
        try:
            with open(self.log_path + 'model_path.txt') as f:
                model_name = f.readlines()[0]
            if self.model_name != model_name:
                self.model_name = model_name
                print('load model')
                self.net.load_state_dict(torch.load(self.log_path+model_name))
                print('load '+self.model_name+' success')
        except:
            pass
        # get step
        q_values = self.predict(state)
        if random.random() < self.epsilon:
            best_action = np.argmax(q_values)
        else:
            candi = [i for i in range(q_values.shape[0])]
            best_action = np.random.choice(candi)
        return best_action

    def eval_step(self, state):
        q_values = self.predict(state)
        best_action = np.argmax(q_values)
        info = {}
        return best_action, info

    def share_memory(self):
        self.net.share_memory()

    def eval(self):
        self.net.eval()

    def parameters(self):
        return self.net.parameters()

    def predict(self, state):
        # Prepare obs and actions
        obs = state['obs'].astype(np.float32)
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
        """
        obs = np.repeat(obs[np.newaxis, :], len(action_keys), axis=0)
        print(obs.shape,action_values.shape)
        values = self.net.forward(torch.from_numpy(obs).to(self.device),torch.from_numpy(action_values).to(self.device))
        return action_keys, values.cpu().detach().numpy()
        """
        q_values_tensor = None
        s = np.repeat(np.expand_dims(state['obs'], axis=0), len(action_values), axis=0)
        stateAction = np.hstack((s, action_values))
        num = np.int(np.ceil(len(action_values)/self.max_split_size))
        for n in range(num):
            if n != num-1:
                tmp = self.net.forward(torch.from_numpy(stateAction[n*self.max_split_size:(n+1)*self.max_split_size])
                                       .to(self.device).to(torch.float32))
            else:
                tmp = self.net.forward(torch.from_numpy(stateAction[n * self.max_split_size:])
                                       .to(self.device).to(torch.float32))
            if q_values_tensor is None:
                q_values_tensor = tmp
            else:
                q_values_tensor = torch.cat((q_values_tensor, tmp))
        q_values = q_values_tensor.cpu().detach().numpy().reshape(len(action_values))
        masked_q_values = -np.inf * np.ones(len(action_values), dtype=float)
        legal_actions = list(state['legal_actions'].keys())
        masked_q_values[legal_actions] = q_values[legal_actions]
        return masked_q_values

    def forward(self, actions):
        return self.net.forward(actions)

    def load_state_dict(self, state_dict):
        return self.net.load_state_dict(state_dict)

    def state_dict(self):
        return self.net.state_dict()

    def set_device(self, device):
        self.device = device

    def gpu_name(self, data_dir, gpu_num, coords_num):
        count_name, data_name = [], []
        for i in range(gpu_num):
            for j in range(coords_num):
                tmp = data_dir+'gpu'+str(i)+'/count'+str(j)+'.pickle'
                count_name.append(tmp)
                tmp = data_dir+'gpu'+str(i)+'/data'+str(j)+'.pickle'
                data_name.append(tmp)
        return count_name, data_name

    def learn(self, memory, memory_size, batch_size, log_path, coords_num,
              epoch, gpu, collect_data_num, data_dir):
        writer = SummaryWriter(log_path)
        global_step = 0
        memory_idx = 0
        count_flag = 0
        change_model_flag = 0
        count_name, data_name = self.gpu_name(data_dir, gpu, coords_num)
        try:
            with open(data_dir+'memory.pickle', 'rb') as f:
                memory_tmp = pickle.load(f)
                memory = memory_tmp['memory']
                memory_idx = memory_tmp['memory_idx']
                global_step = memory_tmp['global_step']
        except:
            print('No saved memory')
        while True:
            # 一共新收集到了多少数据
            gpu_count = []
            train_flag = 1
            total_memory_num = 0
            try:
                for name in count_name:
                    with open(name, 'rb') as f:
                        tmp = pickle.load(f)
                        gpu_count.append(tmp)
            except:
                train_flag = 0
            total_memory_num = sum(gpu_count)

            if total_memory_num>=collect_data_num and train_flag:
                # 读取数据
                data_flag = 1
                for name in data_name:
                    try:
                        with open(name, 'rb') as f:
                            tmp = pickle.load(f)
                            if type(tmp) != int:
                                if data_flag:
                                    data = tmp
                                    data_flag = 0
                                else:
                                    data = np.vstack((data, tmp))
                        with open(name, 'wb') as f:
                            pickle.dump(0, f)
                    except:
                        print('cannot find ' + name)
                        continue
                for name in count_name:
                    with open(name, 'wb') as f:
                        pickle.dump(0, f)
                # 导入数据
                for i in range(data.shape[0]):
                    memory_idx += 1
                    if memory_idx == memory_size:
                        memory_idx -= memory_size
                        count_flag = 1
                    count = memory_size if count_flag else memory_idx
                    memory[memory_idx] = data[i]
                print('新增数据：'+str(data.shape[0])+'，记忆库：'+str(count))
                # 保存数据
                with open(data_dir+'memory.pickle', 'wb') as f:
                    memory_tmp = {'memory':memory, 'memory_idx': memory_idx, 'global_step': global_step}
                    pickle.dump(memory_tmp, f)
                # 这一次的循环轮数
                tmp_step = int(np.ceil(min(count, memory_size)*epoch/(batch_size*gpu)))
                # 训练
                print("开始训练，global step is: " + str(global_step))
                self.epsilon = self.epsilon+self.epsilon_increment if self.epsilon<0.999 else self.epsilon 
                for _ in range(tmp_step):
                    if count <= batch_size:
                        if count >= 0:
                            batch_idx = np.random.choice(a=count, size=count, replace=False)
                    else:
                        batch_idx = np.random.choice(a=min(count, memory_size), size=batch_size, replace=False)
                    batch_data = memory[batch_idx, :]
                    if batch_data.shape[0] != 0:
                        values = self.net.forward(torch.from_numpy(batch_data[:, :-1]).to(self.device).to(torch.float32))
                        targets = torch.from_numpy(batch_data[:, -1]).to(self.device).to(torch.float32)
                        loss = self.loss(values, targets)
                        self.optim.zero_grad()
                        loss.backward()
                        self.optim.step()
                        # 保存模型
                        if global_step % 50 == 0:
                            change_model_flag = 1
                            model_name = 'FcModel_' + str(global_step) + '_' + str(loss.cpu().detach().numpy()) + '.pth'
                            print('step: '+str(global_step)+' loss: '+str(loss.cpu().detach().numpy()))
                            torch.save(self.net.state_dict(), log_path + model_name)
                        writer.add_scalar('loss', loss, global_step)
                        global_step += 1
                memory_idx += 1
                print("结束训练，global step is: " + str(global_step))
                if change_model_flag:
                    change_model_flag = 0
                    with open(log_path+'model_path.txt', 'w') as f:
                        f.write(model_name)
        writer.close()
