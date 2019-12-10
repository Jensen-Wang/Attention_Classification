import sys

sys.path.extend(["../../", "../", "./"])
import torch
import pickle
import time
import argparse
import gensim
from torch import nn
from datetime import datetime
from attention.lstm_attention.net.lstm_attention import LSTM_attention
from attention.lstm_attention.data.dataset import dataset1



def now():
    return str(time.strftime('%Y-%m-%d %H:%M:%S'))


# ======================================================================================================================
# 模型评估
# ======================================================================================================================

def get_acc(output, label):
    total = output.shape[0]
    _, pred_label = torch.max(output, 1)

    num_correct = (pred_label == label).sum().item()

    return num_correct / total


# ======================================================================================================================
# 训练模型
# ======================================================================================================================
def train(model, train_data, valid_data, config, optimizer, criterion):
    model = model.to(config.device)
    prev_time = datetime.now()

    for epoch in range(config.num_epochs):
        model = model.train()
        train_loss = 0
        train_acc = 0

        for im, label in train_data:
            im = im.to(config.device)
            label = label.long().to(config.device)

            # forward
            output = model(im)

            loss = criterion(output, label)
            # backward
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            train_acc += get_acc(output, label)

        cur_time = datetime.now()
        h, remainder = divmod((cur_time - prev_time).seconds, 3600)
        m, s = divmod(remainder, 60)
        time_str = "Time %02d:%02d:%02d" % (h, m, s)

        if valid_data is not None:
            valid_loss = 0
            valid_acc = 0
            model = model.eval()
            for im, label in valid_data:
                with torch.no_grad():
                    im = im.to(config.device)
                    label = label.long().to(config.device)

                output = model(im)
                loss = criterion(output, label)
                valid_loss += loss.item()
                valid_acc += get_acc(output, label)
            epoch_str = (
                    "Epoch %d. Train Loss: %f, Train Acc: %f, Valid Loss: %f, Valid Acc: %f, "
                    % (epoch, train_loss / len(train_data),
                       train_acc / len(train_data), valid_loss / len(valid_data),
                       valid_acc / len(valid_data)))
        else:
            epoch_str = ("Epoch %d. Train Loss: %f, Train Acc: %f, " %
                         (epoch, train_loss / len(train_data),
                          train_acc / len(train_data)))
        prev_time = cur_time
        print(epoch_str + time_str)



def emb(model_path):

    model = gensim.models.KeyedVectors.load_word2vec_format(model_path, binary=False)

    wv = model.wv
    vocab_list = wv.index2word

    """将单词的下标和单词组成dict"""
    word2id = {}
    for id, word in enumerate(vocab_list):
        word2id[word] = id

    vectors = wv.vectors

    return word2id,vectors

# ======================================================================================================================
# 主函数
# ======================================================================================================================

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    # parameter of train set
    parser.add_argument('-seed', default=2019, help="seed")
    parser.add_argument('-freeze', default=False)
    parser.add_argument('-embedding1',help="embedding model",required=True)
    parser.add_argument('-embedding2',help="embedding model")
    parser.add_argument('-train_data_path', required=True)
    parser.add_argument('-train_pos', type=int, required=True)
    parser.add_argument('-train_neg', type=int, required=True)
    parser.add_argument('-batch_size', default=64)
    parser.add_argument('-test_data_path')
    parser.add_argument('-test_pos',type=int)
    parser.add_argument('-test_neg',type=int)
    parser.add_argument('-fix_len', required=True,type=int)
    parser.add_argument('-learning_rate', default=0.01)
    parser.add_argument('-dropout', default=0.1)
    parser.add_argument('-num_classes', default=2)
    parser.add_argument('-hidden_dims', default=100)
    parser.add_argument('-rnn_layers', default=2)
    parser.add_argument('-vocab_size' )
    parser.add_argument('-dim',default=50)
    parser.add_argument('-num_epochs',default=100)
    parser.add_argument('-weight_decay', default=0.0)
    parser.add_argument('-init', default=True)

    opt = parser.parse_args()
    opt.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(opt)

    # gpu测试
    gpu = torch.cuda.is_available()
    print("GPU available: ", gpu)
    print("CuDNN: ", torch.backends.cudnn.enabled)
    print('GPUs：', torch.cuda.device_count())

    torch.set_num_threads(4)
    torch.manual_seed(opt.seed)
    torch.cuda.manual_seed(opt.seed)
    torch.cuda.manual_seed_all(opt.seed)

    w2id,vector=emb(opt.embedding1)
    word2vec = torch.Tensor(vector)

    if opt.embedding2:
        w2id2,vec=emb(opt.embedding2)
        glove = torch.Tensor(vec)
        model = LSTM_attention(weight1=word2vec, weight2=glove, opt=opt)
    else:
        model = LSTM_attention(weight1=word2vec, weight2=None, opt=opt)

    d=dataset1(opt,w2id)
    if opt.test_data_path:
        train_data = d.get_trainset(opt)
        validate_data = d.get_testset(opt)
    else:
        train_data, validate_data = d.get_splite_data(opt)

    criterion = nn.CrossEntropyLoss()

    if opt.freeze:
        model_parameters = filter(lambda p: p.requires_grad, model.parameters())
    else:
        model_parameters = model.parameters()

    optimzier = torch.optim.Adam(model_parameters, lr=opt.learning_rate, weight_decay=opt.weight_decay)

    train(model, train_data, validate_data, opt, optimzier, criterion)