# systemd
**systemd** – это подсистема инициализации и управления службами в Linux. С её помощью возможна настройка автоматического запуска сервисов и мониторинга ресурсов.

## Порядок инициализации
1. Открыть файл _hibot.service_ и подставить в него данные о расположении скрипта. При необходимости произвести дополнительную настройку юнита.
2. Поместить _hibot.service_ в директорию `/etc/systemd/system`.
3. Запустить терминал и последовательно выполнить следующие команды:
```
systemctl daemon-reload
systemctl start hibot
systemctl enable hibot
systemctl status hibot
```
**Примечание:** Если доступ к серверу осуществляется не от **root**, то для исполнения потребуется получить права суперпользователя. Для этого добавьте `sudo` в начале каждой строки.

4. Проверить появившийся в терминале статус сервиса. Он должен выглядеть так: `Active: active (running)`.