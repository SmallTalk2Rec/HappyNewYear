import pandas as pd
from sklearn.metrics import accuracy_score, roc_auc_score, recall_score, precision_score

import torch
from torch.utils.data import TensorDataset, DataLoader, Dataset
import torch.nn as nn
from torch.optim import Adam

from dataloaders import DeepCoNN_loader
from models import MF, DeepCoNN
from trainers import DeepCoNN_test, DeepCoNN_train
from modules import arg_parsing

import wandb


# args 선언
print('arg parsing')
args = arg_parsing()
print('device:',args.device)


# W&B
wandb.init(
    project="DeepCoNN",  # 프로젝트 이름
    name=args.model_path,  # 실험 이름
    config=vars(args)
)

# 파일 임포트
print('DATA LOADing...')
data = DeepCoNN_loader(args)

n_users, n_items = len(data['user2id']), len(data['item2id'])
model = DeepCoNN(len(data['vocab2id']), data['max_len'], args)

model.to(args.device)
optimizer = Adam(model.parameters(), lr=args.lr)


# trainer
print('TRAINing...')
DeepCoNN_train(model, data['train_dataloader'], data['valid_dataloader'], optimizer, args)

# test
print('TESTing...')
DeepCoNN_test(model, data['test_dataloader'], optimizer, args)

# model file 저장
torch.save(model.state_dict(), args.model_path)
print(f"Model saved to {args.model_path}")

wandb.save("model.pth")  # W&B에 모델 파일 저장

# 7. W&B 종료
wandb.finish()