#!/usr/bin/env python3
"""
Scripts to train a model for it.

Usage:
    train.py (train) [--tub=<tub1,tub2,..tubn>]  (--model=<model>) [--base_model=<base_model>] [--no_cache]

Options:
    -h --help        Show this screen.
    --tub TUBPATHS   List of paths to tubs. Comma separated. Use quotes to use wildcards. ie "~/tubs/*"
"""
import os
from docopt import docopt

from keras import KerasLinear
from datastore import TubGroup

#TRAINING
BATCH_SIZE = 128
TRAIN_TEST_SPLIT = 0.8
CAR_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH = os.path.join(CAR_PATH, 'data')
new_model_path = os.path.join(CAR_PATH, '\models\mymodel')
tub_names = os.path.join(CAR_PATH, 'tub')

#def train(tub_names, new_model_path, base_model_path=None):
def train():

    """
    use the specified data in tub_names to train an artifical neural network
    saves the output trained model as model_name
    """
    X_keys = ['cam/image_array']
    y_keys = ['user/angle', 'user/throttle']

#    new_model_path = os.path.expanduser(new_model_path)

    kl = KerasLinear()

#    if base_model_path is not None:
#        base_model_path = os.path.expanduser(base_model_path)
#        kl.load(base_model_path)

#    print('tub_names', tub_names)
#    if not tub_names:
#        tub_names = os.path.join(DATA_PATH, '*')
    tubgroup = TubGroup(tub_names)
    train_gen, val_gen = tubgroup.get_train_val_gen(X_keys, y_keys,
                                                    batch_size=BATCH_SIZE,
                                                    train_frac=TRAIN_TEST_SPLIT)

    total_records = len(tubgroup.df)
    total_train = int(total_records * TRAIN_TEST_SPLIT)
    total_val = total_records - total_train
    print('train: %d, validation: %d' % (total_train, total_val))
    steps_per_epoch = total_train // BATCH_SIZE
    print('steps_per_epoch', steps_per_epoch)

    kl.train(train_gen,
             val_gen,
             saved_model_path=new_model_path,
             steps=steps_per_epoch,
             train_split=TRAIN_TEST_SPLIT)


if __name__ == '__main__':

#    args = docopt(__doc__)

#    tub = args['--tub']
#    new_model_path = args['--model']
#    base_model_path = args['--base_model']
#    cache = not args['--no_cache']
#   train(tub, new_model_path, base_model_path)
    train()





