## Описание команды import_csv

Команда нужна для автоматической пакетной загрузки
данных из CSV файлов (папка ./static/data/*.csv).

Заливка данных осуществляется в **пустую базу**.
Перед выполнением скрипта нужно применить миграции

```
python ./api_yamdb/manage.py migrate
python ./api_yamdb/manage.py makemigrations
```

### Команда

```
python ./api_yamdb/manage.py import_csv 
```