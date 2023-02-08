
import os
import stable_baselines3 as sb3
from stable_baselines3.common.logger import configure
import gym
import sys
import os
import time
import chessEnv
env = chessEnv.ChessEnv(white=True)
model = sb3.PPO.load("modelsV2",env=env)



times = []
for i in range(20):
    obs = env.reset()
    done = False
    s = time.time()
    while not done:
        time.sleep(1)
        env.render()
        action, states = model.predict(obs, deterministic=True)
        print(action)
        print(env.moves[action])
        # print(action)
        obs, reward, done, info = env.step(action)
        # print(obs)
    cnt = time.time() - s  
    times.append(cnt)
env.close()

cnt = 0
for i in times:
    cnt = cnt + i
print(cnt/len(times))
print(len(times))
