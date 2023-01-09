import numpy as np
import torch
from torch import nn

class HardSwish(nn.Module):
    def __init__(self, inplace=True):
        super(HardSwish, self).__init__()
        self.relu6 = nn.ReLU6(inplace)

    def forward(self, x):
        return x*self.relu6(x+3)/6

class fcModel(nn.Module):
    def __init__(self,
                 mlp_layers=[1024, 1024, 1024, 1024, 512]):
        super().__init__()
        input_dim = 551
        layer_dims = [input_dim] + mlp_layers
        fc = []
        for i in range(len(layer_dims)-1):
            fc.append(nn.Linear(layer_dims[i], layer_dims[i+1]))
            if i >= 2:
                fc.append(HardSwish())
            else:
                fc.append(nn.Hardtanh())
        fc.append(nn.Linear(layer_dims[-1], 1))
        fc.append(nn.Hardtanh())
        self.fc_layers = nn.Sequential(*fc)

    def forward(self, x):
        value = self.fc_layers(x).flatten()
        return value
