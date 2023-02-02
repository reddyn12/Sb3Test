import os
import stable_baselines3 as sb3
import gym
import sys
import os
import time


env = gym.make("CartPole-v1")
env.reset()

model = sb3.PPO("MlpPolicy", env, verbose=1)
# .194 - 10
# .197 - 100
# .237 - 1000
# 1.250 - 10000
# 3.488 - 100000
model.learn(1000)
times = []
for i in range(100):
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


