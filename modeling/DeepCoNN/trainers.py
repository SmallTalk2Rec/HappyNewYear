from sklearn.metrics import accuracy_score, recall_score, roc_auc_score
from tqdm import tqdm
import torch.nn.functional as F
import wandb


def MF_trainer(args, data, model, loss_fn, optimizer, train_log):

    for epoch in tqdm(range(1,args.epochs+1), desc='epochs'):

        # train
        train_loss = 0
        for user,item,fresh in data['train_dataloader']:
            
            user = user.to(args.device)
            item = item.to(args.device)
            fresh = fresh.to(args.device)

            yhat = model(user, item)

            optimizer.zero_grad()
            loss = loss_fn(yhat, fresh)
            loss.backward()
            optimizer.step()

            train_loss += loss.detach().cpu()

        print(f'{epoch}th epoch\ntrain_loss: {train_loss/len(data["train_dataloader"])}')
        train_log.append({f'{epoch}th epoch': train_loss/len(data["train_dataloader"])})

        # validate    
        valid_loss,result,answer = 0,[],[]
        for user,item,fresh in data['valid_dataloader']:

            user = user.to(args.device)
            item = item.to(args.device)
            fresh = fresh.to(args.device)

            yhat = model(user,item)
            loss = loss_fn(yhat, fresh)
            valid_loss += loss.item()
            yhat_bin = (yhat >= 0.5).int()

            answer += fresh.tolist()
            result += yhat_bin.tolist()

        ac = accuracy_score(answer, result)
        rec = recall_score(answer, result)
        roc = roc_auc_score(answer, result)

        print(f'valid_loss: {valid_loss/len(data["valid_dataloader"])}\naccuracy: {ac}\nrecall: {rec}\nroc: {roc}')
    
    

def MF_test(args, data, model):

    answer = []
    result = []
    for user,item,fresh in data['test_dataloader']:

        user = user.to(args.device)
        item = item.to(args.device)
        fresh = fresh.to(args.device)

        yhat = model(user,item)
        yhat_bin = (yhat >= 0.5).detach().cpu().int()

        answer += fresh.tolist()
        result += yhat_bin.tolist()

    ac = accuracy_score(answer, result)
    rec = recall_score(answer, result)
    roc = roc_auc_score(answer, result)

    print(f'---TEST SCORE---\naccuracy: {ac}\nrecall: {rec}\nroc: {roc}')





# Model training example
def DeepCoNN_train(model, train_loader, valid_loader, optimizer, args):
    criterion = F.mse_loss
    epochs = args.epochs
    count = 0
    old_loss = 1e9

    for epoch in range(epochs):

        # train
        train_loss = 0
        model.train()
        for movie_id, movie_review, user_id, user_review, ratings in train_loader:
            
            movie_review = movie_review.to(args.device)
            # movie_id = movie_id.to(args.device)
            user_review = user_review.to(args.device)
            # user_id = user_id.to(args.device)
            ratings = ratings.to(args.device)

            # training
            optimizer.zero_grad()
            predictions = model(movie_review, user_review)
            loss = criterion(predictions, ratings.squeeze(1).float()) #FM

            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        # valid
        valid_loss = 0
        model.eval()
        for movie_id, movie_review, user_id, user_review, ratings in valid_loader:
            
            movie_review = movie_review.to(args.device)
            # movie_id = movie_id.to(args.device)
            user_review = user_review.to(args.device)
            # user_id = user_id.to(args.device)
            ratings = ratings.to(args.device)

            predictions = model(movie_review, user_review)
            loss = criterion(predictions, ratings.squeeze(1).float()) #FM
            valid_loss += loss.item()

        print(f"Epoch {epoch+1}/{epochs}, Train Loss: {train_loss/len(train_loader):.4f}, Valid Loss: {valid_loss/len(valid_loader):.4f}")
        wandb.log({ "train_loss": train_loss/len(train_loader), "epoch": epoch+1, "valid_loss": valid_loss/len(valid_loader) })


        # Early Stop
        if old_loss > valid_loss: count += 1
        else: count = 0
        
        if count >= 4:
            print(f'Early Stop on {epoch}th Epoch')
            break

        old_loss = valid_loss


def DeepCoNN_test(model, test_loader, optimizer, args):
    model.eval()
    criterion = F.mse_loss
    epochs = args.epochs

    test_loss = 0
    for movie_id, movie_review, user_id, user_review, ratings in test_loader:
        user_reviews = user_reviews.to(args.device)
        item_reviews = item_reviews.to(args.device)
        ratings = ratings.to(args.device)

        optimizer.zero_grad()
        predictions = model(user_reviews, item_reviews)
        loss = criterion(predictions, ratings.float()) #FM
        test_loss += loss.item()

    print(f"TEST LOSS: {test_loss/len(test_loader):.4f}")
    args.test_score = test_loss / len(test_loader)
    args.model_path = f'DeepCoNN_{args.test_score}.pt'