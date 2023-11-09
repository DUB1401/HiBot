from Source.BotManager import BotManager
from telebot import types

import requests
import telebot

# Создаёт разметку меню администратора.
def CreateMenu(BotProcessor: BotManager) -> types.ReplyKeyboardMarkup:
	# Статус коллекционирования.
	Collect = "" if BotProcessor.getData()["collect-media"] == False else " (остановить)"
	# Статус бота.
	Status = "🔴 Остановить" if BotProcessor.getData()["active"] == True else "🟢 Возобновить"
	
	# Меню администратора.
	Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
	# Генерация кнопок.
	Edit = types.KeyboardButton("✍ Редактировать")
	Add = types.KeyboardButton("🖼️ Медиа" + Collect)
	Button = types.KeyboardButton("🕹️ Кнопка")
	URL = types.KeyboardButton("🔗 URL")
	Preview = types.KeyboardButton("🔍 Предпросмотр")
	Stop = types.KeyboardButton(Status)
	# Добавление кнопок в меню.
	Menu.add(Edit, Add, Button, URL, Preview, Stop, row_width = 2)
	
	return Menu

# Загружает изображение.
def DownloadImage(Token: str, Bot: telebot.TeleBot, FileID: int) -> bool:
	# Состояние: успешна ли загрузка.
	IsSuccess = False
	# Получение сведений о файле.
	FileInfo = Bot.get_file(FileID) 
	# Получение имени файла.
	Filename = FileInfo.file_path.split('/')[-1]
	# Список расширений изображений.
	ImagesTypes = ["jpeg", "jpg", "png", "gif"]
	
	# Если вложение имеет расширение изображения.
	if Filename.split('.')[-1] in ImagesTypes:

		# Загрузка файла.
		Response = requests.get("https://api.telegram.org/file/bot" + Token + f"/{FileInfo.file_path}")
	
		# Если запрос успешен.
		if Response.status_code == 200:
		
			# Открытие потока записи.
			with open(f"Data/{Filename}", "wb") as FileWriter:
				# Запись файла.
				FileWriter.write(Response.content)
				# Переключение статуса.
				IsSuccess = True		
		
	return IsSuccess

# Экранирует символы при использовании MarkdownV2 разметки.
def EscapeCharacters(Post: str) -> str:
	# Список экранируемых символов. _ * [ ] ( ) ~ ` > # + - = | { } . !
	CharactersList = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']

	# Экранировать каждый символ из списка.
	for Character in CharactersList:
		Post = Post.replace(Character, "\\" + Character)

	return Post