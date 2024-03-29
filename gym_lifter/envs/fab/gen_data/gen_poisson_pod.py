import numpy as np
import random
import os
from tqdm import tqdm


# FAB data generation without the existence of POD


num_lots = 6624                 # expected number of arrived lots during a single simulation
sim_time = 86400.               # data for 24 hrs

# parameter \lambda for Poisson process
# S_n : time when n-th lot arrival occurs
# Here we assume S_n = X_1 + ... X_n, where each X_k is an i.i.d. sample drawn from Exponential(\lambda):
# P(X_k > x) = e^{-\lambda x}, x > 0
# N_t : # of lots arrived until time t which is defined by
# N_t = \max(n >= 0 : S_n <=> t)
# Since N_t >= n iff S_n <= t, we deduce that N_t follows Poisson(\lambda t)
# Thus, E(N_t) = \lambda t
# See also Billingsley, 1979.
missions = [(2, 3, 0), (3, 2, 0), (3, 6, 0), (6, 3, 0), (6, 2, 0), (2, 6, 0), (6, 2, 1), (2, 6, 1)]
non_pod_p23 = 1.5 / 20.
non_pod_p36 = 3. / 20.
non_pod_p62 = 5. / 20.
pod = .5 / 20.
prob = [non_pod_p23, non_pod_p23, non_pod_p36, non_pod_p36, non_pod_p62, non_pod_p62, pod, pod]
num = [num_lots * p for p in prob]
lam = [n_lots / sim_time for n_lots in num]
beta = [1. / ell for ell in lam]

num_scenarios = 200     # number of total scenarios


for scenario in tqdm(range(num_scenarios)):
    data = {mission: [] for mission in missions}
    num_arrival = 0
    elapsed_t = 0.
    for i in range(len(missions)):
        mission = missions[i]
        mission_list = list(mission)
        b = beta[i]
        elapsed_t = 0.

        while elapsed_t < sim_time:
            dt = np.random.exponential(b)
            elapsed_t += dt
            data[mission].append([elapsed_t] + mission_list)
            num_arrival += 1

        # remove the final one, since its command time exceeds 24:00:00
        data[mission].pop()
        data[mission] = np.array(data[mission])
        num_arrival -= 1

    entire_episode = np.concatenate([data[mission] for mission in missions], axis=0)
    entire_episode = entire_episode[entire_episode[:, 0].argsort()]     # sort entire data by command time

    # save generated data
    data_cmd = entire_episode[:, 0]
    data_from = entire_episode[:, 1]
    data_to = entire_episode[:, 2]
    data_pod = entire_episode[:, 3]

    dir_path = '../assets/day_pod/scenario{}/'.format(scenario)
    os.makedirs(dir_path, exist_ok=True)

    np.save(dir_path + 'data_cmd.npy', np.array(data_cmd))
    np.save(dir_path + 'data_from.npy', np.array(data_from, dtype=np.int))
    np.save(dir_path + 'data_to.npy', np.array(data_to, dtype=np.int))
    np.save(dir_path + 'data_pod.npy', np.array(data_pod, dtype=np.int))

    if scenario == 0:
        # example of generated data as csv file
        data = np.array([data_cmd, data_from, data_to, data_pod]).T
        np.savetxt(dir_path + 'data.csv', data, delimiter=',')
