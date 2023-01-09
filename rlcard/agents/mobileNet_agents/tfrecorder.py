import tensorflow as tf
import numpy as np
import os
import pdb
import random
import pickle
from rlcard.agents.mobileNet_agents import input_data

#生成整数型的属性（feature）
def int64_feature(value) :
#   ＃（注意这个函数，下面有用到的。。。）
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

def float_feature(value) :
#   ＃（注意这个函数，下面有用到的。。。）
    return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))

#生成字符串型的属性（feature）
def bytes_feature(value):
        # ＃（注意这个函数，下面有用到的。。。）
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=value))

def floats_feature(value):
    return tf.train.Feature(float_list=tf.train.FloatList(value=value))


def convert_to_tfrecord(writer, data):
    try:
        label = data[-1]
        image_raw = data[:-1]
        example = tf.train.Example(features=tf.train.Features(feature={
                                        'label': float_feature(label),
                                        'image_raw': floats_feature(image_raw)}))
        writer.write(example.SerializeToString())
    except IOError as e:
        print('Could not read: data')
        print('error: %s' %e)
        print('Skip it!\n')

def read_and_decode(filename, n_epochs = None):
    #根据文件名生成一个队列
    filename_queue = tf.train.string_input_producer([filename], num_epochs = n_epochs )

    reader = tf.TFRecordReader()
    _, serialized_example = reader.read(filename_queue)   #返回文件名和文件
    features = tf.parse_single_example(serialized_example,
                                       features={
                                           'label': tf.FixedLenFeature([], tf.float32),
                                           'image_raw' : tf.VarLenFeature(tf.float32)})

    # img = tf.decode_raw(features['image_raw'], tf.uint8)
    img = tf.sparse_tensor_to_dense(features['image_raw'], default_value=0)
    img = tf.reshape(img, [551])
    img = tf.cast(img, tf.float32)
    label = tf.cast(features['label'], tf.float32)

    return img, label


if __name__ == "__main__" :
    test_TFRecorder_path = './Train.tfrecords'
    train_TFRecorder_path = './Test.tfrecords'

    filename =  (test_TFRecorder_path)
    test_writer = tf.python_io.TFRecordWriter(filename)
    filename =  (train_TFRecorder_path)
    train_writer = tf.python_io.TFRecordWriter(filename)

    coordList = ['coord'+str(i) for i in range(1, 91)]

    total = 0
    for coord in coordList:
        nameList = os.listdir('./'+coord)
        total += len(nameList)
    cnt = 0
    for coord in coordList:
        nameList = os.listdir('./'+coord)
        for name in nameList:
            cnt += 1
            print(cnt, '/', total)
            nameDir = './' + coord + '/' + name
            with open(nameDir, 'rb') as f:
                tmp = pickle.load(f)
                for i in range(tmp.shape[0]):
                    if random.random() < 0.7:
                        convert_to_tfrecord(train_writer, tmp[i])
                    else:
                        convert_to_tfrecord(test_writer, tmp[i])
    test_writer.close()
    train_writer.close()



