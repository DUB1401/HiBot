from telebot import types

import requests
import telebot

# Формирует текст сообщения об ошибке.
def CreateExceptionMessage(Type: str, ExceptionData: Exception, Data: dict = dict()) -> str:
	# Экранирование символов.
	Type = EscapeCharacters(Type)
	ExceptionData = EscapeCharacters(str(ExceptionData))
	# Диагностические сведения.
	DataList = ""
	
	# Для каждого ключа.
	for Key in Data.keys():
		# Если нет заголовка, то добавить его.
		if DataList == "": DataList = "📋 *Данные*\n"
		# Составить строку.
		DataList += EscapeCharacters(str(Key)) + ": " + "_" + EscapeCharacters(str(Data[Key])) + "_\n"

	# Текст сообщения об ошибке.
	Message = f"⚠️ *ОШИБКА*\n\n*Тип:* {Type}\n\n{DataList}\n*Исключение:* {ExceptionData}"
	# Обрезка сообщения.
	Message = Message[:2048]
	
	return Message

# Создаёт разметку меню администратора.
def CreateMenu(BotProcessor: any) -> types.ReplyKeyboardMarkup:
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