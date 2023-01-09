# Reinforcement-Learning-based-on-Strategy-Card-Games



This is a personal project. There's a time I really want to know how reinforcement learning work and how to implement reinforcement learning. Thus, I put many efforts into the project. The whole project is based on [RLCard](https://rlcard.org/), a toolkit for reinforcement learning in card games.

First, I wrote the whole rules of the game in `rlcard/games/axie`. Then, I set up two agents that simulate two players playing games. Once they make an action, the program simulates the game till the end. The winner get a score of 1, and the other one gets -1. They run each action n times, then average n scores to get a relatively accurate and reasonable score as the groundtruth of the action. The program saves the current situation and score in `data/gpuX`. After collecting m final scores, the program trains the model and gets a better agent. When the program keeps doing the previous two steps, collecting data and training the model, we can make the agent smarter and better decisions. The strategy is straightforward because the action sample is larger than any other card game. Therefore, a strategy like Monte Carlo Tree Search is impossible here.

In this project, simulation costs most of the time, so we need to use multiprocessing to accelerate the process (8 GPUs and 120 cores CPUs). I want to share my work, though this is a personal project, and I have a tight budget, so I cannot train the model to get the best result. I spent five months on the project, with no previous reinforcement learning foundation, until I implemented this one, so I still feel the achievement. 
