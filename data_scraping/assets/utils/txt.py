def append_to_txt(file_name, data):
    """
    데이터를 /로 구분하여 txt 파일에 추가합니다.
    """
    line = "/".join(map(str, data)) + "\n"  # 데이터를 /로 구분하여 한 줄 생성
    with open(file_name, "a", encoding="utf-8") as file:
        file.write(line)
    # print(f"'{line.strip()}'이 {file_name}에 추가되었습니다.")