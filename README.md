Для развёртывания проекта требуется:
1. Клонировать репозиторий
2. Установить Docker 
3. В директории 'Back' создать файл .env:

  POSTGRES_PASSWORD = 'пароль от базы данных'
  POSTGRES_USER = 'имя root пользователя бд'
  POSTGRES_DB = 'название бд'

4. В директории 'Front' создать файл .env:
  BOT_TOKEN = 'токен вашего бота'

5. Далее запустить проект с помощью команд:
  docker compose build
  docker compose up

