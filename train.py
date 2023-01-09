''' An example of training a reinforcement learning agent on the environments in RLCard '''
import argparse
import rlcard
import numpy as np
import multiprocessing as mp
from rlcard.agents.mobileNet_agents import model

def main(args):
    env = rlcard.make(args.env)
    agent = model.DMCAgent(state_shape=env.state_shape[0],
                           action_shape=env.action_shape[0],
                           max_split_size=args.max_split_size,
                           load_model=args.log_dir+args.model_name if args.model_name is not None else None,
                           device_ids=args.device_ids,
                           log_path = args.log_dir)
    agents = [agent, agent]
    agent.share_memory()
    ctx = mp.get_context('spawn')
    memory = np.zeros((args.memory_size, 552))
    coord = ['coord'+str(i) for i in range(args.coord_num)]
    pauses = ['pause'+str(i) for i in range(args.coord_num)]
    coords = []
    for i in range(args.coord_num):
        exec(coord[i] +'=ctx.Process(target=env.runLoop, args=(agents, args.loop_num, i,'
                       'args.memory_size,args.data_dir, args.device_ids[0]))')
        exec(coord[i] + '.start()')
        exec('coords.append('+coord[i]+')')
    while True:
        agent.learn(memory, args.memory_size, args.batch_size, args.log_dir, coords, args.other_coords, pauses,
                    args.epoch, args.gpu_num, args.train_after_collect_num_of_data, args.data_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser("DQN/NFSP example in RLCard")
    parser.add_argument('--env', type=str, default='axie')
    parser.add_argument('--log_dir', type=str, default='experiments/axie/')
    parser.add_argument('--data_dir', type=str, default='data/')
    parser.add_argument('--model_name', type=str, default=None)
    parser.add_argument('--coord_num', type=int, default=1) 
    parser.add_argument('--other_coords', type=int, default=8) 
    parser.add_argument('--cpu_coords', type=int, default=45) 
    parser.add_argument('--loop_num', type=int, default=50)
    parser.add_argument('--memory_size', type=int, default=50000) 
    parser.add_argument('--batch_size', type=int, default=2048)
    parser.add_argument('--epoch', type=int, default=4)
    parser.add_argument('--gpu_num', type=int, default=7) 
    parser.add_argument('--max_split_size', type=int, default=2048)
    parser.add_argument('--train_after_collect_num_of_data', type=int, default=1024)#
    parser.add_argument('--device_ids', type=list, default=[0])

    args = parser.parse_args()
    main(args)
