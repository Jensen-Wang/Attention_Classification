import torch
import numpy as np
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split


class data1():
    def __init__(self,opt,word_index_dict):
        self.opt=opt
        self.word_index_dict=word_index_dict

    # 返回该词的index，将每条记录转化成由index组成的list，判断其长度不足的补0
    def word2index(self,word):
        """将一个word转换成index"""
        if word in self.word_index_dict:
            return self.word_index_dict[word]
        else:
            return 0


    def sentence2index(self,sentence):
        """将一个句子转换成index的list，并截断或补零"""
        word_list = sentence.strip().split()
        index_list = list(map(self.word2index, word_list))
        len_sen = len(index_list)
        if len_sen < self.opt.fix_len:
            index_list = index_list + [0] * (self.opt.fix_len - len_sen)
        else:
            index_list = index_list[:self.opt.fix_len]
        return index_list

    # 划分数据集
    def get_splite_data(self):
        f = open(self.opt.train_data_path)
        documents = f.readlines()
        sentence = []
        for words in documents:
            s = self.sentence2index(words)
            sentence.append(s)

        x = np.array(sentence)

        """取出标签"""
        y = [0] * self.opt.train_pos + [1] * self.opt.train_neg
        y = np.array(y)

        train_x, val_x, train_y, val_y = train_test_split(
            x, y, test_size=0.1, random_state=0)

        train_data = TensorDataset(torch.from_numpy(train_x), torch.from_numpy(train_y))
        valid_data = TensorDataset(torch.from_numpy(val_x), torch.from_numpy(val_y))

        train_loader = DataLoader(train_data, shuffle=False, batch_size=self.opt.batch_size)
        valid_loader = DataLoader(valid_data, shuffle=False, batch_size=self.opt.batch_size)

        return train_loader, valid_loader


    # 划分数据集2
    def get_splite_data2(self):
        f = open(self.opt.train_data_path)
        documents = f.readlines()
        sentence = []
        for words in documents:
            s = self.sentence2index(words)
            sentence.append(s)

        x = np.array(sentence)

        """取出标签"""
        y = [0] * self.opt.train_pos + [1] * self.opt.train_neg
        y = np.array(y)

        l = []
        for i in range(len(y)):
            l.append((x[i], y[i]))

        total=self.opt.train_pos+self.opt.train_neg

        train_dataset, test_dataset = torch.utils.data.random_split(l, [int(total * 0.8), int(total * 0.2)])
        train_data = DataLoader(train_dataset, self.opt.batch_size, False)
        test_data = DataLoader(test_dataset, self.opt.batch_size, False)

        return train_data, test_data


    # ======================================================================================================================
    # 获得训练集
    # ======================================================================================================================
    def get_trainset(self):
        f = open(self.opt.train_data_path)
        documents = f.readlines()
        sentence = []
        for words in documents:
            s = self.sentence2index(words)
            sentence.append(s)

        x = np.array(sentence)

        """取出标签"""
        y = [0] * self.opt.train_pos + [1] * self.opt.train_neg
        y = np.array(y)

        train_data = TensorDataset(torch.from_numpy(x), torch.from_numpy(y))
        train_loader = DataLoader(train_data, shuffle=False, batch_size=self.opt.batch_size)

        return train_loader


    # ======================================================================================================================
    # 获得测试集
    # ======================================================================================================================
    def get_testset(self):
        f = open(self.opt.test_data_path)
        documents = f.readlines()
        sentence = []
        for words in documents:
            s = self.sentence2index(words)
            sentence.append(s)

        x = np.array(sentence)

        """取出标签"""
        y = [0] * self.opt.test_pos + [1] * self.opt.test_neg
        y = np.array(y)

        test_data = TensorDataset(torch.from_numpy(x), torch.from_numpy(y))
        test_loader = DataLoader(test_data, shuffle=False, batch_size=self.opt.batch_size)

        return test_loader
