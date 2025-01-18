import pandas as pd
from torch.utils.data import TensorDataset, DataLoader, Dataset
import torch
import numpy as np

from sklearn.model_selection import train_test_split
import json


def load_data(args):

    data = {}
    data['X_train'] = pd.read_csv(args.data_path + 'MF_X_train.csv')
    data['Y_train'] = pd.read_csv(args.data_path + 'MF_Y_train.csv')

    data['X_valid'] = pd.read_csv(args.data_path + 'MF_X_val.csv')
    data['Y_valid'] = pd.read_csv(args.data_path + 'MF_Y_val.csv')

    data['X_test'] = pd.read_csv(args.data_path + 'MF_X_test.csv')
    data['Y_test'] = pd.read_csv(args.data_path + 'MF_Y_test.csv')
    
    return data



def MF_loader(args, data):
    '''
    유저와 아이템의 id만 뱉는 방식의 데이터로더
    [전처리 + dataset + dataloader]

    criticName: uid (userid)
    id: iid (itemid)
    fresh/rotten: 1/0 (binary)

    return: LongTensor([uid number, iid number, 1/0])
    '''
    

    # LabelEncoding -> Out Of Dictionary problem 세게 있네
    user2id = {u:i for i,u in enumerate(data['X_train']['criticName'].unique())}
    item2id = {item:i for i,item in enumerate(data['X_train']['id'].unique())}
    fresh2id = {'fresh':1, 'rotten':0}

    id2user = {i:u for i,u in user2id.items()}
    id2item = {i:item for i,item in item2id.items()}
    id2fresh = {1:'fresh', 0:'rotten'}

    data['X_train']['criticName'] = data['X_train']['criticName'].map(user2id)
    data['X_train']['id'] = data['X_train']['id'].map(item2id)
    data['Y_train'] = data['Y_train']['reviewState'].map(fresh2id)

    data['X_valid']['criticName'] = data['X_valid']['criticName'].map(user2id)
    data['X_valid']['id'] = data['X_valid']['id'].map(item2id)
    data['Y_valid'] = data['Y_valid']['reviewState'].map(fresh2id)
    
    data['X_test']['criticName'] = data['X_test']['criticName'].map(user2id)
    data['X_test']['id'] = data['X_test']['id'].map(item2id)
    data['Y_test'] = data['Y_test']['reviewState'].map(fresh2id)

    
    # LongTensor화
    train_dataset = TensorDataset(torch.LongTensor(data['X_train']['criticName'].values), torch.LongTensor(data['X_train']['id'].values), torch.FloatTensor(data['Y_train'].values))
    valid_dataset = TensorDataset(torch.LongTensor(data['X_valid']['criticName'].values), torch.LongTensor(data['X_valid']['id'].values), torch.FloatTensor(data['Y_valid'].values))
    test_dataset = TensorDataset(torch.LongTensor(data['X_test']['criticName'].values), torch.LongTensor(data['X_test']['id'].values), torch.FloatTensor(data['Y_test'].values))

    train_dataloader = DataLoader(train_dataset, batch_size=args.batch_size)
    valid_dataloader = DataLoader(valid_dataset, batch_size=args.batch_size)
    test_dataloader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False)

    data['train_dataloader'], data['valid_dataloader'], data['test_dataloader'] = train_dataloader, valid_dataloader, test_dataloader
    data['user2id'], data['item2id'], data['id2user'], data['id2item'], data['fresh2id'], data['id2fresh'] = user2id, item2id, id2user, id2item, fresh2id, id2fresh

    return data

## DeepCoNN
class ReviewDataset(Dataset):
    '''
    DeepCoNN review 데이터 활용하기
    '''

    def __init__(self, user_reviews, item_reviews, ratings):
        self.user_reviews = user_reviews
        self.item_reviews = item_reviews
        self.ratings = ratings

    def __len__(self):
        return len(self.ratings)

    def __getitem__(self, idx):
        return self.user_reviews[idx], self.item_reviews[idx], self.ratings[idx]
    


def DeepCoNN_loader(args):

    '''
    데이터 전처리 및 배치화
    필요데이터: label화된 리뷰텍스트 데이터
    dataloader: [movie_id, movie_review, user_id, user_review, rating]
    '''

    data = {}

    ## 전처리 된 데이터 파일 불러오기
    ratings = pd.read_json("ratings_reviews_encoded.json", orient="records", lines=True)
    user2id, id2user, movie2id, id2movie, vocab2id, id2vocab = load_json('user2id.json'), load_json('id2user.json'), load_json('movie2id.json'), load_json('id2movie.json'), load_json('vocab2id.json'), load_json('id2vocab.json')

    # Dataloader
    max_len = min(max(ratings['movie_review'].map(len)), max(ratings['user_review'].map(len)))
    ratings['movie_review'] = ratings['movie_review'].apply(
        lambda x: x + [0] * (max_len - len(x)) if len(x) < max_len else x[:max_len])
    ratings['user_review'] = ratings['user_review'].apply(
        lambda x: x + [0] * (max_len - len(x)) if len(x) < max_len else x[:max_len])

    # train-test split
    movie_train, movie_test, user_train, user_test, rating_train, rating_test = train_test_split(ratings[['MovieID','movie_review']], ratings[['UserID','user_review']], ratings[['Rating']], test_size=0.2)
    movie_train, movie_valid, user_train, user_valid, rating_train, rating_valid = train_test_split(movie_train, user_train, rating_train, test_size=0.2)
    data['movie_train'], data['user_train'], data['rating_train'], data['movie_valid'], data['user_valid'], data['rating_valid'], data['movie_test'], data['user_test'], data['rating_test'] = movie_train, user_train, rating_train, movie_valid, user_valid, rating_valid, movie_test, user_test, rating_test
    
    print('Dataset')
    train_dataset = MyDataset(data['movie_train'], data['user_train'], data['rating_train'])
    valid_dataset = MyDataset(data['movie_valid'], data['user_valid'], data['rating_valid'])
    test_dataset = MyDataset(data['movie_test'], data['user_test'], data['rating_test'])
    print('DataLoader')
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    valid_loader = DataLoader(valid_dataset, batch_size=args.batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=True)

    data['train_dataloader'], data['valid_dataloader'], data['test_dataloader'] = train_loader, valid_loader, test_loader
    data['user2id'], data['item2id'], data['vocab2id'], data['id2user'], data['id2item'], data['id2vocab'], data['max_len'] = user2id, movie2id, vocab2id, id2user, id2movie, id2vocab, max_len
    
    return data


# JSON파일로 딕셔너리 로드
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


# Custom Dataset 정의
class MyDataset(Dataset):
    def __init__(self, movie, user, rating):

        # 리뷰
        self.movie_review = [torch.LongTensor(seq) for seq in movie["movie_review"]]
        self.user_review = [torch.LongTensor(seq) for seq in user["user_review"]]
        
        # ID (활용X)
        self.movie_id = movie["MovieID"].apply(lambda x: torch.LongTensor([x])).tolist()
        self.user_id = user["UserID"].apply(lambda x: torch.LongTensor([x])).tolist()

        # 평점
        self.rating = rating["Rating"].apply(lambda x: torch.FloatTensor([x])).tolist()
            

    def __len__(self):
        return len(self.movie_review)

    def __getitem__(self, idx):
        return self.movie_id[idx], self.movie_review[idx], self.user_id[idx], self.user_review[idx], self.rating[idx]