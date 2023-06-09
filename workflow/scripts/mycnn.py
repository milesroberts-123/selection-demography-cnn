# load packages
print("Loading packages...")
import sys, os
import numpy as np
import pandas as pd
from PIL import Image
import keras
import matplotlib.pyplot as plt
import tensorflow as tf
#from keras.optimizers import SGD

# Check if GPUs are available
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

# define parameters
path = "data/images/"
batch_size = 32
epochs = 100
patience = 5
slim_params = "../config/parameters.tsv"
weightFolderName = "data/weights"
finalModelName = "best_cnn.h5"

# split data into training, testing, and validation
print("Reading table of parameters...")
slim_params = pd.read_table(slim_params)

print("Splitting table into training, validation, and testing...")
train_params = slim_params[slim_params["split"] == "train"]
val_params = slim_params[slim_params["split"] == "val"]
test_params = slim_params[slim_params["split"] == "test"]

#print("Splitting response variable into training, validation, and testing...")
#train_y = train_params["sweepS"] 
#val_y = val_params["sweepS"]
#test_y = test_params["sweepS"]

train_ids = list(train_params["ID"])
val_ids = list(val_params["ID"])
test_ids = list(test_params["ID"])

print("Loading images and converting to RGB...")
train_images = np.asarray([np.asarray(Image.open(path + "slim_" + str(x) + ".png").convert('RGB'))/255 for x in train_ids if os.path.exists(path + "slim_" + str(x) + ".png")])
val_images = np.asarray([np.asarray(Image.open(path + "slim_" + str(x) + ".png").convert('RGB'))/255 for x in val_ids if os.path.exists(path + "slim_" + str(x) + ".png")])
test_images = np.asarray([np.asarray(Image.open(path + "slim_" + str(x) + ".png").convert('RGB'))/255 for x in test_ids if os.path.exists(path + "slim_" + str(x) + ".png")])

print("Shapes of training, validation, and testing images:")
print(train_images.shape)
print(val_images.shape)
print(test_images.shape)

# subset to only simulations which you have images for
print("Subsetting response variable to only finished simulations...")
#train_y = np.asarray([train_y[(x-1)] for x in train_ids if os.path.exists(path + "slim_" + str(x) + ".png")])
#val_y = np.asarray([val_y[(x-1)] for x in val_ids if os.path.exists(path + "slim_" + str(x) + ".png")])
#test_y = np.asarray([test_y[(x-1)] for x in test_ids if os.path.exists(path + "slim_" + str(x) + ".png")])
train_y = np.asarray([slim_params.iloc[(x-1), 5] for x in train_ids if os.path.exists(path + "slim_" + str(x) + ".png")])
val_y = np.asarray([slim_params.iloc[(x-1), 5] for x in val_ids if os.path.exists(path + "slim_" + str(x) + ".png")])
test_y = np.asarray([slim_params.iloc[(x-1), 5] for x in test_ids if os.path.exists(path + "slim_" + str(x) + ".png")])

print(train_y.shape)
print(val_y.shape)
print(test_y.shape)

#print(train_y)
#print(val_y)
#print(test_y)

print("Converting response to binary outcome...")
train_y[np.where(train_y == 0.5)] = 1
val_y[np.where(val_y == 0.5)] = 1
test_y[np.where(test_y == 0.5)] = 1
#train_y = (train_y == 0.5)
#val_y = (val_y == 0.5)
#test_y = (test_y == 0.5)

# load tables to get position information from slim
#train_pos = np.asarray([np.asarray(pd.read_table("data/tables/slim_" + str(x) + ".table")) for x in train_ids if os.path.exists("data/tables/slim_" + str(x) + ".table")])
#val_pos = np.asarray([np.asarray(pd.read_table("data/tables/slim_" + str(x) + ".table")) for x in val_ids if os.path.exists("data/tables/slim_" + str(x) + ".table")])
#test_pos = np.asarray([np.asarray(pd.read_table("data/tables/slim_" + str(x) + ".table")) for x in test_ids if os.path.exists("data/tables/slim_" + str(x) + ".table")])

#print("Shapes of training, validation, and testing positions:")
#print(train_pos.shape)
#print(val_pos.shape)
#print(test_pos.shape)

# Create model with functional API
print("Creating model...")
input_A = keras.layers.Input(shape = [128,128,3], name = "images")
conv1 = keras.layers.Conv2D(filters = 32, kernel_size = 7, strides = 2, padding = "same", activation = "relu", input_shape = [128,128,3])(input_A)
pool1 = keras.layers.MaxPooling2D(2)(conv1)
pool1 = keras.layers.Dropout(0.5)(pool1)
conv2 = keras.layers.Conv2D(filters = 64, kernel_size = 3, strides = 1, padding = "same", activation = "relu")(pool1)
pool2 = keras.layers.MaxPooling2D(2)(conv2)
pool2 = keras.layers.Dropout(0.5)(pool2)
flat = keras.layers.Flatten()(pool2)
dense = keras.layers.Dense(64, activation = "relu")(flat)
dropped = keras.layers.Dropout(0.25)(dense)
output = keras.layers.Dense(1, name = "output", activation = "sigmoid")(dropped)
model = keras.Model(inputs = [input_A], outputs = [output])

# compile model
print("Compiling model...")
#model.compile(loss='mean_squared_error', optimizer='adam')
model.compile(optimizer='adam', loss="binary_crossentropy", metrics = ["accuracy", tf.keras.metrics.TruePositives(), tf.keras.metrics.TrueNegatives(), tf.keras.metrics.FalsePositives(), tf.keras.metrics.FalseNegatives()])
#opt = SGD(lr=0.01) # create optimizer
#model.compile(loss = "binary_crossentropy", optimizer = opt, metrics = ["accuracy"])

# add callbacks: early stopping and saving at checkpoints
earlystop = keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0.0, patience=patience, verbose=0, mode='auto')
checkpoint = keras.callbacks.ModelCheckpoint(weightFolderName, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
callbacks = [earlystop, checkpoint]

# fit model
print("Fitting model...")
history = model.fit(train_images, train_y, batch_size=batch_size, epochs=epochs, verbose=1, validation_data=(val_images, val_y), callbacks=callbacks)

# evaluate total error in model
print("Evaluating model...")
model.evaluate(test_images, test_y)

# test model
print("Testing model...")
val_pred = model.predict(val_images)
test_pred = model.predict(test_images)

print(val_y)
print(val_pred)

#print(test_y)
#print(test_pred)
print(keras.metrics.confusion_matrix(test_y, test_pred))

# plot predictions against real values
#plt.scatter(test_y, final_pred)
#plt.xlabel("Real selection coefficient")
#plt.ylabel("Predicted selection coefficient")
#plt.plot([0,0.05], [0,0.05], color='k', linestyle='-', linewidth=2)
#plt.savefig('test_real_vs_predictions.png')
#plt.close()

# plot training data predictions against real values
#train_pred = model.predict(train_images)
#plt.scatter(train_y, train_pred)
#plt.xlabel("Real selection coefficient")
#plt.ylabel("Predicted selection coefficient")
#plt.plot([0,0.05], [0,0.05], color='k', linestyle='-', linewidth=2)
#plt.savefig('train_real_vs_predictions.png')
#plt.close()

# save model
print("Saving final model...")
model.save(finalModelName)

print("Done! :)")
