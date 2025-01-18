import pandas as pd
from sklearn.preprocessing import LabelEncoder

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader, Dataset

import torch
import torch.nn as nn
import torch.nn.functional as F




class MF(nn.Module):
    def __init__(self, n_users:int, n_items:int, args):
        super().__init__()
        self.user_embed = nn.Embedding(n_users+1, args.embed_dims)
        self.item_embed = nn.Embedding(n_items+1, args.embed_dims)
        self.sigmoid = nn.Sigmoid()

        nn.init.xavier_uniform_(self.user_embed.weight.data)
        nn.init.xavier_uniform_(self.item_embed.weight.data)


    def forward(self, user, item):
        """
        uTv: dot product 연산
        """

        xu = self.user_embed(user).reshape(-1,1,64)
        xi = self.item_embed(item).reshape(-1,64,1)

        if not xu.is_contiguous():
            xu = xu.contiguous()
        if not xi.is_contiguous():
            xi = xi.continguous()

        result = torch.bmm(xu,xi)
        result = self.sigmoid(result)

        return result.reshape(-1)



## Review 활용 모델
class DeepCoNN(nn.Module):

    def __init__(self, vocab_size, max_len, args): 
        embed_dim, num_filters, kernel_size = args.embed_dim, args.num_filters, args.kernel_size
        super(DeepCoNN, self).__init__()

        # Constants
        self.user_embed_size = max_len - kernel_size + 1
        self.item_embed_size = max_len - kernel_size + 1
        print('kernel_size:', kernel_size)
        print('embed_size:', self.user_embed_size, self.item_embed_size)

        # Embedding
        self.embedding = nn.Embedding(vocab_size+1, embed_dim) #0:padding #Shape: (batch_size, embed_dim) (256,128) #데이터가 지금 sequence

        # CNN for reviews
        self.user_cnn = nn.Conv2d(1, num_filters, (kernel_size, embed_dim)) # kernel_size: window_size
        self.item_cnn = nn.Conv2d(1, num_filters, (kernel_size, embed_dim))

        self.user_mlp = nn.Linear(self.user_embed_size, self.user_embed_size) #seq_len - kernel_size + 1)
        self.item_mlp = nn.Linear(self.item_embed_size, self.item_embed_size) #seq_len - kernel_size + 1)

        # output
        self.FM = FactorizationMachine()
        

    def forward(self, item_reviews, user_reviews):

        self.user_seq_len = user_reviews.size(1)
        self.item_seq_len = item_reviews.size(1)

        # Embedding
        user_emb = self.embedding(user_reviews).unsqueeze(1)  # Shape: (batch, 1, seq_len, embed_dim)
        item_emb = self.embedding(item_reviews).unsqueeze(1)  # Shape: (batch, 1, seq_len, embed_dim)

        ## Context Aggregate
        # CNN & max-pooling for user reviews
        user_features = F.relu(self.user_cnn(user_emb)).squeeze(3)  # Shape: (batch, num_filters, seq_len)
        user_features = F.max_pool1d(user_features.permute(0,2,1), user_features.size(1)).squeeze(2)  # Shape: (batch, seq_len - kernel_size + 1)
        user_features = self.user_mlp(user_features) # Shape: (batch, seq_len - kernel_size + 1)

        # CNN & max-pooling for item reviews
        item_features = F.relu(self.item_cnn(item_emb)).squeeze(3)  # Shape: (batch, num_filters, seq_len/window_size)
        item_features = F.max_pool1d(item_features.permute(0,2,1), item_features.size(1)).squeeze(2)  # Shape: (batch, seq_len - kernel_size + 1)
        item_features = self.item_mlp(item_features) # Shape: (batch, seq_len - kernel_size + 1)

        ## Combine
        # Concat & FM
        combined_features = torch.concat([user_features.unsqueeze(1), item_features.unsqueeze(1)], dim=1) # (batch, 2, embed_size)
        output = self.FM(combined_features)

        return output
    

class FactorizationMachine(torch.nn.Module):

    def __init__(self, reduce_sum=True):
        super().__init__()
        self.reduce_sum = reduce_sum

    def forward(self, x):
        """
        :param x: Float tensor of size ``(batch_size, num_fields, embed_dim)``
        """
        square_of_sum = torch.sum(x, dim=1) ** 2
        sum_of_square = torch.sum(x ** 2, dim=1)
        ix = square_of_sum - sum_of_square

        if self.reduce_sum:
            ix = torch.sum(ix, dim=1)
            
        return 0.5 * ix