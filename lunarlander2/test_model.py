import os
# for keras the CUDA commands must come before importing the keras libraries
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
import gym
from gym import wrappers
import numpy as np
from keras.models import load_model

# evaluate model

if __name__ == '__main__':
    env = gym.make('LunarLander-v2')
    env = wrappers.Monitor(env, "tmp/lunar-lander-ddqn-2",
                            video_callable=lambda episode_id: True, force=True)
    model = load_model("ddqn_model.h5")

    scores = []
    n_games = 1

    for i in range(n_games):
        done = False
        score = 0
        observation = env.reset()
        while not done:
            # add a dimension to observation
            # state = observation[np.newaxis, :]
            state = np.array([observation])

            actions = model.predict(state)
            action = np.argmax(actions)

            observation, reward, done, info = env.step(action)

            score += reward

        scores.append(score)
        avg_score = np.mean(scores[max(0, i-100):(i+1)])
        print('episode: ', i,'score: %.2f' % score,
              ' average score %.2f' % avg_score)
        
    print(scores)