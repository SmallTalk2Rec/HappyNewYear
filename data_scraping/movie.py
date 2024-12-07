from tqdm import tqdm
from multiprocessing import Pool
from assets.scraping.watcha.movie import get_watch_infos
from assets.utils.driver import get_driver
from assets.utils.json import read_json, write_json  # 필요한 유틸 함수 임포트

CUSTOM_FILE_PATH = "./data/custom.json"
MOVIE_FILE_PATH = "./data/movie.json"


def worker(movie_ids):
    """
    워커 프로세스에서 작업을 수행.
    """
    driver = get_driver()

    data = read_json(MOVIE_FILE_PATH)
    
    for movie_id in tqdm(movie_ids):    
        data = read_json(MOVIE_FILE_PATH)
        
        if movie_id not in data.keys():
            watcha_infos = get_watch_infos(driver, movie_id, n_comment=None)
            data[movie_id] = watcha_infos
            
            write_json(MOVIE_FILE_PATH, data)
            
    driver.quit()

def main():
    # JSON 파일 로드
    custom_data = read_json(CUSTOM_FILE_PATH)
    
    movie_ids = list(custom_data['yKZx3yykDv4dJ']['movies'].keys())
    
    # 이미 처리된 movie_id 제거
    movie_ids_to_process = [movie_id for movie_id in movie_ids if movie_id not in custom_data.keys()]
    
    # 멀티 프로세싱 설정
    num_processes = 4  # 사용할 프로세스 수
    chunk_size = len(movie_ids_to_process) // num_processes
    chunks = [movie_ids_to_process[i:i + chunk_size] for i in range(0, len(movie_ids_to_process), chunk_size)]
    
    with Pool(processes=num_processes) as pool:
        # 각 프로세스에서 독립적으로 작업 수행
        pool.map(worker, chunks)

if __name__ == "__main__":
    main()





