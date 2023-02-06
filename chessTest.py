from hashlib import new
import os
import stable_baselines3 as sb3
from stable_baselines3.common.logger import configure
import gym
import sys
import os
import time
import chessEnv


env = chessEnv.ChessEnv()
env.reset()
tmp_path = "logs"
new_logger = configure(tmp_path, ["stdout", "csv", "tensorboard"])
model = sb3.PPO("MlpPolicy", env, verbose=1)
model.set_logger(new_logger)
# print(model.action_space, "model actions space")
# print(model.observation_space, "model obs space")
for i in range(100):
    print(model.action_space.sample())


# print(model.observation_space.shape, "shapes models")

model.learn(total_timesteps=10, progress_bar=True)
print("done train")
times = []
for i in range(10):
    obs = env.reset()
    done = False
    s = time.time()
    while not done:
        env.render()
        action, _ = model.predict(obs)
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

