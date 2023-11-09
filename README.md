# HiBot
**HiBot** – это бот [Telegram](https://telegram.org/), отправляющий приветственные сообщения пользователям, подавшим заявку на вступление в закрытую группу или канал. Он поддерживает стили Telegram, прикрепление вложений и кнопку перехода по ссылке.

## Порядок установки и использования
1. Загрузить последний релиз. Распаковать.
2. Установить Python версии не старше 3.10.
3. В среду исполнения установить следующие пакеты: [dublib](https://github.com/DUB1401/dublib), [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI?ysclid=loq3f2bmuz181940716).
```
pip install git+https://github.com/DUB1401/dublib
pip install pyTelegramBotAPI
```
Либо установить сразу все пакеты при помощи следующей команды, выполненной из директории скрипта.
```
pip install -r requirements.txt
```
4. Настроить скрипт путём редактирования _Settings.json_.
5. Назначить бота администратором группы или канала.
6. Открыть директорию со скриптом в терминале. Можно использовать метод `cd` и прописать путь к папке, либо запустить терминал из проводника.
7. Указать для выполнения главный файл скрипта `main.py`, перейти в Telegram, отправить в чат с ботом команду `/start` и установленный в настройках пароль администратора, после чего настроить приветственное сообщение.
8. Для автоматического запуска службы рекомендуется провести инициализацию скрипта через [systemd](https://github.com/systemd/systemd) (пример [здесь](https://github.com/DUB1401/HiBot/tree/main/systemd)) на Linux или путём добавления его в автозагрузку на Windows.

# Команды
```
/debug
```
Выводит отладочную информацию.
___
```
/delbutton
```
Отключает прикрепляемую к приветственному сообщению кнопку.
___
```
/start
```
Инициализирует работу бота и запускает процесс авторизации.
___
```
/unattach
```
Удаляет все вложения.

# Settings.json
```JSON
"token": ""
```
Сюда необходимо занести токен бота Telegram (можно получить у [BotFather](https://t.me/BotFather)).
___
```JSON
"premium": false
```
Здесь указывается, имеется ли у хозяина бота Premium-подписка. Влияет на максимальную длину сообщения.
___
```JSON
"password": "1234"
```
Пароль для авторизации администратора.
___
```JSON
"active": true
```
Если отключить, бот перестанет приветствовать пользователей, подавших заявку на встпуление.
___
```JSON
"message": ""
```
Текст приветственного сообщения. Поддерживает HTML разметку, допустимую в Telegram.
___
```JSON
"button": null
```
Заголовок кнопки.
___
```JSON
"link": null
```
Ссылка, по которой пользователю будет предложено перейти после нажатия кнопки.
___
```JSON
"collect-media": false
```
Состояние: идёт ли в данный момент приём вложений.
___
```JSON
"admins": []
```
Список ID аккаунтов Telegram, имеющих права администратора.

_Copyright © DUB1401. 2023._