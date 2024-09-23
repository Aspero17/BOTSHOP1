# Загрузка токена из файла
def load_token(file_path="mytoken.txt"):
    with open(file_path, "r") as file:
        return file.read().strip()

API_TOKEN = load_token()
