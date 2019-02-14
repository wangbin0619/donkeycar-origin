""""

keras.py

functions to run and train autopilots using keras

"""

from tensorflow.python.keras.layers import Input
from tensorflow.python.keras.models import Model, load_model
from tensorflow.python.keras.layers import Convolution2D,MaxPooling2D
from tensorflow.python.keras.layers import Dropout, Flatten, Dense
from tensorflow.python.keras.callbacks import ModelCheckpoint, EarlyStopping,ReduceLROnPlateau,TensorBoard
from tensorflow.python.keras.utils import plot_model

class KerasPilot:

    def load(self, model_path):
        print("Keras Load Model {} and plotted in model.png".format(model_path))
        self.model = load_model(model_path)
        plot_model(self.model, show_shapes=True, to_file='model.png')

    def shutdown(self):
        pass

    def train(self, train_gen, val_gen,
              saved_model_path, epochs=100, steps=100, train_split=0.8,
              verbose=1, min_delta=.0005, patience=5, use_early_stop=True):
        """
        train_gen: generator that yields an array of images an array of

        """

        # checkpoint to save model after each epoch
        save_best = ModelCheckpoint(saved_model_path,
                                    monitor='val_loss',
                                    verbose=verbose,
                                    save_best_only=True,
                                    mode='auto')

        # stop training if the validation error stops improving.
        early_stop = EarlyStopping(monitor='val_loss',
                                   min_delta=min_delta,
                                   patience=patience,
                                   verbose=verbose,
                                   mode='auto')

        # reduce the learning rate if validation error not longer improved
        reduce_lr = ReduceLROnPlateau(monitor='val_loss',
                                      factor=0.2,
                                      patience=patience-2,
                                      min_lr=0.001,
                                      verbose=verbose,
                                      mode='auto')

        tensorboard = TensorBoard(log_dir='/home/wangbin/mycar/logs',
                                  histogram_freq=0,
                                  batch_size=32,
                                  write_graph=True,
                                  write_grads=False,
                                  write_images=True)
#                                  embeddings_freq=0,
#                                  embeddings_layer_names=None,
#                                  embeddings_metadata=None,
#                                  embeddings_data=None,
#                                  update_freq='epoch')

        callbacks_list = [save_best]

        if use_early_stop:
            callbacks_list.append(early_stop)

        callbacks_list.append(reduce_lr)
        callbacks_list.append(tensorboard)

        hist = self.model.fit_generator(
            train_gen,
            steps_per_epoch=steps,
            epochs=epochs,
            verbose=verbose,
            validation_data=val_gen,
            callbacks=callbacks_list,
            validation_steps=steps * (1.0 - train_split) / train_split)
        return hist


class KerasLinear(KerasPilot):
    def __init__(self, model=None, num_outputs=None, *args, **kwargs):
        super(KerasLinear, self).__init__(*args, **kwargs)
        if model:
            self.model = model
        elif num_outputs is not None:
            self.model = default_linear()
        else:
            self.model = default_linear()
        self.model.summary()

    def run(self, img_arr):
        img_arr = img_arr.reshape((1,) + img_arr.shape)
        outputs = self.model.predict(img_arr)
        # print(len(outputs), outputs)
        steering = outputs[0]
        throttle = outputs[1]
        return steering[0][0], throttle[0][0]


def default_linear():
    img_in = Input(shape=(120, 160, 3), name='img_in')
    x = img_in

    # Convolution2D class name is an alias for Conv2D
#    x = Convolution2D(filters=24, kernel_size=(5, 5), strides=(1, 1), activation='relu')(x)
#    x = MaxPooling2D((2, 2), padding='same')(x)
#    x = Convolution2D(filters=32, kernel_size=(5, 5), strides=(1, 1), activation='relu')(x)
#    x = MaxPooling2D((2, 2), padding='same')(x)
#    x = Convolution2D(filters=64, kernel_size=(5, 5), strides=(1, 1), activation='relu')(x)
#    x = MaxPooling2D((2, 2), padding='same')(x)
#    x = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu')(x)
#    x = MaxPooling2D((2, 2), padding='same')(x)
#    x = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu')(x)

    # Convolution2D class name is an alias for Conv2D
    x = Convolution2D(filters=24, kernel_size=(5, 5), strides=(2, 2), activation='relu')(x)
    x = Convolution2D(filters=32, kernel_size=(5, 5), strides=(2, 2), activation='relu')(x)
    x = Convolution2D(filters=64, kernel_size=(5, 5), strides=(2, 2), activation='relu')(x)
    x = Convolution2D(filters=64, kernel_size=(3, 3), strides=(2, 2), activation='relu')(x)
    x = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu')(x)

    x = Flatten(name='flattened')(x)
    x = Dense(units=100, activation='linear')(x)
    x = Dropout(rate=.1)(x)
    x = Dense(units=50, activation='linear')(x)
    x = Dropout(rate=.1)(x)
    # categorical output of the angle
    angle_out = Dense(units=1, activation='linear', name='angle_out')(x)

    # continous output of throttle
    throttle_out = Dense(units=1, activation='linear', name='throttle_out')(x)

    model = Model(inputs=[img_in], outputs=[angle_out, throttle_out])

    model.compile(optimizer='adam',
                  loss={'angle_out': 'mean_squared_error',
                        'throttle_out': 'mean_squared_error'},
                  loss_weights={'angle_out': 0.5, 'throttle_out': .5})

    return model
