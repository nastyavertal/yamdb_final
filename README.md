# YAMDB_FINAL
![example event parameter](https://github.com/nastyavertal/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg?event=push)

Предназначен для тренировки и закрепления на практике навыков CI и CD.

# api_yamdb
Проект YaMDb собирает отзывы пользователей на различные произведения.
***
### Возможности:
* Регистрация (по ник-нейму и электронной почте)
* Получение токена (по ник-нейму и коду подтверждения почты)
* Написание отзыва для произведений 
* Оценка произведений по шкале от 1 до 10
* Комментирование отзыва
* Админ может создавать/удалять жанры, категории, произведения
* Админ может назначать модераторов из пользователей
***

***
### Как запустить проект:

**Сделать fork данного репозитория**

**Переместится к себе в репозиторий**

**Склонировать репозиторий на локальную машину**
git clone https://github.com/<ваш_username>/yamdb_final.git

**В настройках своего репозитория добавьте Secrets GutHub Actions переменные окружения(Settings -> Secrets -> Actions -> New repository secret) по списку:**

```
БД:
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=postgres
   POSTGRES_USER=
   POSTGRES_PASSWORD=
   DB_HOST=db
   DB_PORT=5432
Docker Hub:
   DOCKER_USERNAME=
   DOCKER_PASSWORD=
   DOCKER_IMAGE=<ваш-логин-на-docker-hub/ваш-репозиторий-на-docker-hub:latest>
Сервер:
   SSH_KEY=<приватный ключ>
   USER=
   HOST=<ip-адрес вашего сервера>
   PASSPHRASE=<если имеется>
Telegram(отправка уведомлений о deploy):
   TELEGRAM_TO=<id своего телеграм-аккаунта>
   TELEGRAM_TOKEN=<токен вашего телеграм-бота>
```

**Заменить Docker image в файле docker-compose.yaml:**

блок контейнера web, заменить значение image:
```
web:
    image: <ваш-логин-на-docker-hub/ваш-репозиторий-на-docker-hub:latest>
```
Подготовка сервера:
* Остановите службу nginx:
```
sudo systemctl stop nginx
```
* Установите docker и docker-compose:
```
   sudo apt update && sudo apt install apt-transport-https ca-certificates curl gnupg-agent software-properties-common -y && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - && sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && sudo apt update && sudo apt install docker-ce -y && sudo systemctl enable docker && sudo curl -L "https://github.com/docker/compose/releases/download/1.28.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose && sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose && docker-compose --version && sudo service docker restart && service docker status
```
Скопируйте файлы docker-compose.yaml и nginx/default.conf из вашего проекта на сервер в home/<ваш_username>/docker-compose.yaml и home/<ваш_username>/nginx/default.conf соответственно.

### Проверка доступности сервиса:
После коммита проекта на github, если всё сделано правильно, то вам придёт уведомление
об успешном деплое проекта на удалённом сервере.

Порект будет доступен по адресам:
* http://<ваш-id-сервера>/api/v1/
* http://<ваш-id-сервера>/admin
* http://<ваш-id-сервера>/redoc

Мои адреса:
* http://51.250.102.213/api/v1/
* http://51.250.102.213/admin
* http://51.250.102.213/redoc


##Автор проекта: 

### Vertal Nastya
```html
e-mail: veeertal@yandex.ru
```
```html
https://github.com/nastyavertal
```

