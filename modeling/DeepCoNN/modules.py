import argparse
from datetime import datetime


def arg_parsing():
        
    parser = argparse.ArgumentParser(description="각종 Hyperparameters")

    parser.add_argument('--data_path', type=str, default='../../rotten_data/')
    parser.add_argument('--lr', type=float, default=0.00001)
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--device', type=str, default='cpu')
    parser.add_argument('--embed_dims', type=int, default=64)
    parser.add_argument('--batch_size', type=int, default=256)
    
    parser.add_argument('--embed_dim', type=int, default=128)
    parser.add_argument('--num_filters', type=int, default=4)
    parser.add_argument('--kernel_size', type=int, default=5)

    args = parser.parse_args()
    
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    args.model_path = f"DeepCoNN_{current_time}.pt"
    
    return args