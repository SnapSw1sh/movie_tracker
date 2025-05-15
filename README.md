# 1 . Клонируем репозиторий
git clone https://github.com/SnapSw1sh/movie_tracker.git
cd demo-project

# 2 . Создаём и активируем виртуальное окружение
#в VS code откройте палитру (Ctrl+Shift+P) → Python: Select Interpreter, выберите Создание виртуальной среды...        
.venv\Scripts\activate

# 3 . Ставим зависимости
pip install -r requirements.txt

# 4 . Накатываем миграции и создаём суперпользователя
python manage.py migrate
python manage.py createsuperuser

# 5 . Запускаем дев-сервер
python manage.py runserver
