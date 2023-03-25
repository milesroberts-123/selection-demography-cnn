# load packages
print("Loading packages...")
import sys, os
import numpy as np
import pandas as pd
from PIL import Image
import keras
#import matplotlib.pyplot as plt

# define parameters
path = "data/images/"
batch_size = 32
epochs = 100
slim_params = "data/parameters.tsv"
weightFileName = "data/weightfile.txt"

#print("Getting paths to input images...")
#image_paths = os.listdir(path)
#image_paths = [path + x for x in image_paths]

#print("List of input images:")
#print(image_paths)

# load the images into a numpy array, normalizing to get values between 0-1
#print("Loading the images to a numpy array")
#images = np.asarray([np.asarray(Image.open(x))/255 for x in image_paths])

#print(images.shape)
#print(images[0].shape)

# plot image to ensure code works correctly
#plt.imshow(images[0])
#plt.savefig('test.jpg')

# split data into training, testing, and validation
print("Reading table of parameters...")
slim_params = pd.read_table(slim_params)

print("Splitting table into training, validation, and testing...")
train_params = slim_params[slim_params["split"] == "train"]
val_params = slim_params[slim_params["split"] == "val"]
test_params = slim_params[slim_params["split"] == "test"]

print("Splitting response variable into training, validation, and testing...")
train_y = train_params["mean"] 
val_y = val_params["mean"]
test_y = test_params["mean"]

train_ids = list(train_params["ID"])
val_ids = list(val_params["ID"])
test_ids = list(test_params["ID"])

print("Loading images...")
train_images = np.asarray([np.asarray(Image.open(path + "slim_" + str(x) + ".jpg"))/255 for x in train_ids if os.path.exists(path + "slim_" + str(x) + ".jpg")])
val_images = np.asarray([np.asarray(Image.open(path + "slim_" + str(x) + ".jpg"))/255 for x in val_ids if os.path.exists(path + "slim_" + str(x) + ".jpg")])
test_images = np.asarray([np.asarray(Image.open(path + "slim_" + str(x) + ".jpg"))/255 for x in test_ids if os.path.exists(path + "slim_" + str(x) + ".jpg")])

print("Shapes of training, validation, and testing images:")
print(train_images.shape)
print(val_images.shape)
print(test_images.shape)

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
conv1 = keras.layers.Conv2D(filters = 16, kernel_size = 5, strides = 2, padding = "same", activation = "relu", input_shape = [128,128,3])(input_A)
pool1 = keras.layers.MaxPooling2D(2)(conv1)
conv2 = keras.layers.Conv2D(filters = 32, kernel_size = 3, strides = 1, padding = "same", activation = "relu")(pool1)
pool2 = keras.layers.MaxPooling2D(2)(conv2)
flat = keras.layers.Flatten()(pool2)
dense = keras.layers.Dense(64, activation = "relu")(flat)
dropped = keras.layers.Dropout(0.25)(dense)
output = keras.layers.Dense(1, name = "output")(dropped)
model = keras.Model(inputs = [input_A], outputs = [output])

# compile model
print("Compiling model...")
model.compile(loss='mean_squared_error', optimizer='adam')

# add callbacks: early stopping and saving at checkpoints
earlystop = keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=3, verbose=0, mode='auto')
checkpoint = keras.callbacks.ModelCheckpoint(weightFileName, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
callbacks = [earlystop, checkpoint]

# fit model
print("Fitting model...")
history = model.fit(train_images, train_y, batch_size=batch_size, epochs=epochs, verbose=1, validation_data=(val_images, val_y), callbacks=callbacks)

# test model
print("Testing model...")
model.predict(test_images)

print("Done! :)")

# convert image to numpy array
# data = np.asarray(image)
#print(type(data))

# summarize shape
# print(data.shape)
