import numpy as np
from utils.player import MCTSPlayer
# import tensorflow as tf
import pickle
import xgboost as xgb
import os
import joblib

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

MAX_ITERS = 200
C = 0.5
ENV_PATH = os.path.join(project_root, 'models', 'best_model_GBDT.pkl')

class Draft:
    """
    class handling state of the draft
    """

    def __init__(self, env_path=ENV_PATH, state=[[],[]], avail_moves=set([]), player=0):
        # self.model = tf.keras.models.load_model(env_path)
        with open(env_path, 'rb') as file:
            self.model = pickle.load(file)
        self.state = state
        self.avail_moves = avail_moves
        self.move_cnt = [len(state[0]), len(state[1])]
        self.player = player  # current player's turn
        self.next_player = int(not bool(player)) # next player turn

    def get_player(self):
        return MCTSPlayer(draft=self, maxiters=MAX_ITERS, c=C)

    def eval(self):
        assert self.end()
        x = np.zeros((1, 139))
        x[0, self.state[0]] = 1
        x[0, self.state[1]] = -1
        # new
        # [0, 24, 115, 116, 117, 118, 122, 124, 125, 127, 130, 131, 132, 133, 134]
        # old
        # [0, 24, 115, 116, 117, 118, 122, 123, 124, 125, 127]

        x = np.delete(x,[0, 24, 115, 116, 117, 118, 122, 124, 125, 127, 130, 131, 132, 133, 134],axis=1)
        radiant_win_rate = self.model.predict_proba(x)[0, 0]
        return radiant_win_rate

    def copy(self):
        """
        make copy of the board
        """
        copy = Draft()
        copy.model = self.model
        copy.state = [self.state[0][:], self.state[1][:]]
        copy.avail_moves = set(self.avail_moves)
        copy.move_cnt = self.move_cnt[:]
        copy.player = self.player
        copy.next_player = self.next_player
        return copy

    def move(self, move):
        """
        take move of form [x,y] and play
        the move for the current player
        """
        self.player = self.next_player
        self.next_player = int(not bool(self.player))
        self.state[self.player].append(move)
        self.avail_moves.remove(move)
        self.move_cnt[self.player] += 1

    def get_moves(self):
        """
        return remaining possible draft moves
        (i.e., where there are no 1's or -1's)
        """
        if self.end():
            return set([])
        return set(self.avail_moves)

    def end(self):
        """
        return True if all players finish drafting
        """
        if self.move_cnt[0] == 5 and self.move_cnt[1] == 5:
            return True
        return False

if __name__ == "__main__":
    # Create an instance of YourClass
    class_instance = Draft()
    print(class_instance.model)
