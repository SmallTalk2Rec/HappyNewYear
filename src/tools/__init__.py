from .selfquery import SelfQueryTool

toolkits = [
    SelfQueryTool(movie_data_path="./data/rotten_tomatoes_movie_df.csv", vectorstore_dir="./data/chroma")
]