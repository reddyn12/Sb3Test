import os
import stable_baselines3 as sb3
import gym
import sys
import os
import time
from stable_baselines3.common.logger import configure


env = gym.make("CartPole-v1")
t = env.reset()
# print(env.observation_space)
# print(env.action_space)
# print(t)
# sys.exit()
tmp_path = "logs"
new_logger = configure(tmp_path, ["stdout", "csv", "tensorboard"])

model = sb3.PPO("MlpPolicy", env, verbose=1)
model.set_logger(new_logger)
# .194 - 10
# .197 - 100
# .237 - 1000
# 1.250 - 10000
# 3.488 - 100000
model.learn(10000, progress_bar=True)
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


