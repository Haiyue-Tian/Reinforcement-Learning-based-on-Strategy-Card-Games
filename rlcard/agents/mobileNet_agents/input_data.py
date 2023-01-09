import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import os
import pdb


def get_path(iftrain) :
        if iftrain == 1:
                path = 'E:/NAS/上海工程技术大学/毕业论文/程序/0 Data/mat/train/'
                TFRecorder_path = 'E:/NAS/上海工程技术大学/毕业论文/程序/0 Data/TFRecorder/Train.tfrecords'
        else:
                path = 'E:/NAS/上海工程技术大学/毕业论文/程序/0 Data/mat/test/'
                TFRecorder_path = 'E:/NAS/上海工程技术大学/毕业论文/程序/0 Data/TFRecorder/Test.tfrecords'

        return path, TFRecorder_path


def mat2py(path,classes) :
        # for k in range(4):
        #         exec("l_%s=k"%(classes[k]))
        #     images = ['/home/tian_hy/Qsync/上海工程技术大学/毕业论文/程序/0 Data/npy/P_N/Ball.npy',
#                         '/home/tian_hy/Qsync/上海工程技术大学/毕业论文/程序/0 Data/npy/P_N/Inner_Race.npy',
#                         '/home/tian_hy/Qsync/上海工程技术大学/毕业论文/程序/0 Data/npy/P_N/Outer_Race.npy',
#                         '/home/tian_hy/Qsync/上海工程技术大学/毕业论文/程序/0 Data/npy/P_N/Normal.npy']
#     labels = [3,1,2,0]
        l_Normal = 0
        l_Inner_Race = 1
        l_Outer_Race = 2
        l_Ball = 3
        Normal = []
        label_Normal = []
        Inner_Race = []
        label_Inner_Race = []
        Outer_Race = []
        label_Outer_Race = []
        Ball = []
        label_Ball = []


        for name in classes:
                file_name = os.listdir(path + name)
                length = len(file_name)
                for i in range(length) :
                        matpath = path + name + '/' + file_name[i]
                        exec("%s.append(matpath)"%name)
                        exec("label_%s.append(l_%s)"%(name,name))


        # 合并image和label
        image_list = np.hstack((locals()[classes[0]], locals()[classes[1]], locals()[classes[2]], locals()[classes[3]] ))
        label1 = 'label_' + classes[0]
        label2 = 'label_' + classes[1]
        label3 = 'label_' + classes[2]
        label4 = 'label_' + classes[3]
        label_list = np.hstack((locals()[label1],locals()[label2],locals()[label3],locals()[label4]))

        #打乱image和label
        temp = np.array([image_list, label_list])
        temp = temp.transpose()
        np.random.shuffle(temp)

        #将所有的img和lab转换成list
        all_image_list = list(temp[:,0])
        all_label_list = list(temp[:,1])
        all_label_list = [int(float(i)) for i in all_label_list]
        label = np.array(all_label_list)
        image = np.array(all_image_list)
        # image = read_mat(all_image_list)
        # # image=tf.convert_to_tensor(image)
        # #=================================================================
        # # get batch 操作
        # #转换类型
        # label = tf.cast(all_label_list, tf.int32)
        return image, label



def get_batch(image, label, batch_size, min_after_dequeue) :
        capacity = min_after_dequeue+3*batch_size
        img, label = tf.train.shuffle_batch([image, label],
                                             batch_size=batch_size,
                                             num_threads=32,
                                             capacity=capacity,
                                             min_after_dequeue=min_after_dequeue)
        img = tf.cast(img, tf.float32)
        return img, label

# image_batch,label_batch = get_batch(total,path,classes,size,BATCH_SIZE,CAPACITY,N_CLASSES)
