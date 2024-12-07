from tqdm import tqdm
from assets.scraping import get_naver_infos, get_watch_infos, get_wiki_infos
from assets.postprocess import get_movie_info
from assets.utils import load_file_from_pickle, save_file_to_pickle, get_driver

movie_id_dict = load_file_from_pickle('./data/movie_id_dict_241013.pkl')
print(movie_id_dict)

movie_names = list(movie_id_dict.keys())

movie_infos = {}

for movie_name in tqdm(movie_names):
    movie_id = movie_id_dict[movie_name]
    
    driver = get_driver()

    watcha_infos = get_watch_infos(driver, movie_id)
    naver_infos = get_naver_infos(driver, movie_name)
    wiki_infos = get_wiki_infos(driver, movie_name)

    movie_info = get_movie_info(movie_name, movie_id, watcha_infos, naver_infos, wiki_infos)
    
    movie_infos[movie_name] = movie_info

    driver.quit()

save_file_to_pickle(movie_infos, './data/movie_infos_241014.pkl')