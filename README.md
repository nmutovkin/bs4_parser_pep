# Проект парсинга pep

Парсер обрабатывает официальный сайт с документацией Python

## Режимы работы

whats-new - Вывод ссылок на список нововведений предыдущих версий Python с указанием авторов
latest-versions - Вывод информации о версиях Python: номер и статус
download - Скачивание архива с документацией Python
pep - Вывод информации о количестве PEP с разными статусами

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
