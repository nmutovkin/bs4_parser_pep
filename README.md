# Парсер PEP

Парсер обрабатывает официальный сайт с документацией Python

## Технологии

* Python
* Beautiful Soup

## Режимы работы

whats-new - Вывод ссылок на список нововведений предыдущих версий Python с указанием авторов

latest-versions - Вывод информации о версиях Python: номер и статус

download - Скачивание архива с документацией Python

pep - Вывод информации о количестве PEP с разными статусами

## Подготовка к локальному запуску

* Клонируем репозиторий на локальный компьютер ```git clone https://github.com/nmutovkin/bs4_parser_pep.git```
* ```cd bs4_parser_pep```
* Создаем и активируем виртуальное окружение python
    ```
    python -m venv venv
    source venv/bin/activate
    ```
* Устанавливаем зависимости ```pip install -r requirements.txt```

## Запуск парсера и аргументы

Запуск: python main.py [-h] [-c] [-o {pretty,file}] {whats-new,latest-versions,download,pep}

обязательный аргумент:
  {whats-new,latest-versions,download,pep}
                        Режимы работы парсера

вспомогательный аргумент:

  -h, --help            show this help message and exit
  
  -c, --clear-cache     Очистка кеша
  
  -o {pretty,file}, --output {pretty,file}
                        Дополнительные способы вывода данных
