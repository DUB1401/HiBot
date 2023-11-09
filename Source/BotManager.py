from dublib.Methods import RemoveHTML, WriteJSON

from telebot import types

import telebot
import enum
import os

# Типы ожидаемых сообщений.
class ExpectedMessageTypes(enum.Enum):
	
	#---> Статические свойства.
	#==========================================================================================#
	# Неопределённое сообщение.
	Undefined = "undefined"
	# Текст сообщения.
	Message = "message"
	# Название кнопки.
	Button = "button"
	# Изображение.
	Image = "image"
	# Ссылка кнопки.
	Link = "link"

# Менеджер данных бота.
class BotManager:
	
	# Сохраняет настройки.
	def __SaveSettings(self):
		# Сохранение настроек.
		WriteJSON("Settings.json", self.__Settings)
	
	# Конструктор.
	def __init__(self, Settings: dict, Bot: telebot.TeleBot):
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Текущий тип ожидаемого сообщения.
		self.__ExpectedType = ExpectedMessageTypes.Undefined
		# Глобальные настройки.
		self.__Settings = Settings.copy()
		# Экземпляр бота.
		self.__Bot = Bot
		
	# Переключает сбор изображений.
	def collect(self, Status: bool):
		# Переключение сбора изображений.
		self.__Settings["collect-media"] = Status
		# Сохранение настроек.
		self.__SaveSettings()
		
	# Отключает бота.
	def disable(self):
		# Переключение активности.
		self.__Settings["active"] = False
		# Сохранение настроек.
		self.__SaveSettings()
		
	# Изменяет текст приветствия.
	def editMessage(self, Text: str):
		# Состояние: корректин ли текст.
		IsCorrected = True
		# Максимальная длина сообщения.
		MaxLength = 1024 if self.__Settings["premium"] == False else 2048
		if len(os.listdir("Data")) == 0: MaxLength = 4096 
		
		# Если сообщение слишком длинное.
		if len(RemoveHTML(Text)) >= MaxLength:
			# Отключение бота.
			self.disable()
			# Переключение состояния.
			IsCorrected = False
			
		else:
			# Запись сообщения.
			self.__Settings["message"] = Text
			# Сохранение настроек.
			self.__SaveSettings()
			
		return IsCorrected
		
	# Включает бота.
	def enable(self):
		# Переключение активности.
		self.__Settings["active"] = True
		# Сохранение настроек.
		self.__SaveSettings()
		
	# Возвращает количество вложений.
	def getAttachmentsCount(self) -> int:
		# Подсчёт количества файлов.
		Count = len(os.listdir("Data"))
		
		return Count
		
	# Возвращает словарь параметров бота.
	def getData(self):
		return self.__Settings.copy()

	# Возвращает тип ожидаемого сообщения.
	def getExpectedType(self) -> ExpectedMessageTypes:
		return self.__ExpectedType
	
	# Возвращает статус бота.
	def getStatus(self):
		return self.__Settings["active"]
	
	# Возвращает состояние коллекционирования.
	def isCollect(self):
		return self.__Settings["collect-media"]
	
	# Выполняет авторизацию администратора.
	def login(self, UserID: int, Password = None):
		# Состояние: является ли пользователь администратором.
		IsAdmin = False

		# Если пользователь уже администратор.
		if Password == None and UserID in self.__Settings["admins"]:
			# Разрешить доступ к функциям.
			IsAdmin = True
			
		return IsAdmin
	
	# Регистрирует пользователя в качестве администратора.
	def register(self, UserID: int):
		# Добавление ID пользователя в список администраторов.
		self.__Settings["admins"].append(UserID)
		# Сохранение настроек.
		self.__SaveSettings()
		
	# Удаляет кнопку.
	def removeButton(self):
		# Удаление данных кнопки.
		self.__Settings["button"] = None
		self.__Settings["link"] = None
		# Сохранение настроек.
		self.__SaveSettings()
		
	# Отправляет сообщение.
	def sendHi(self, ChatID: int):
		# Список файлов.
		Files = os.listdir("Data")[:10]
		# Контейнер кнопки.
		Buttons = None
		
		# Если есть вложения.
		if len(Files) > 0:
			# Список медиа вложений.
			Attachments = list()
			
			# Для каждого файла.
			for Index in range(0, len(Files)):
				
				# Дополнить вложения файлом.
				Attachments.append(
					types.InputMediaPhoto(
						open("Data/" + Files[Index], "rb"), 
						caption = self.__Settings["message"] if Index == 0 else "",
						parse_mode = "HTML"
					)
				)
				
			# Отправка медиа группы: приветствие нового подписчика.
			self.__Bot.send_media_group(
				ChatID,
				media = Attachments
			)
			
		else:
			
			# Если кнопка описана полностью.
			if self.__Settings["button"] != None and self.__Settings["link"] != None:
				# Создание кнопки ссылки.
				Buttons = types.InlineKeyboardMarkup()
				Button = types.InlineKeyboardButton(self.__Settings["button"], self.__Settings["link"])
				Buttons.add(Button)

			# Отправка сообщения: приветствие нового подписчика.
			self.__Bot.send_message(
				ChatID,
				text = self.__Settings["message"],
				parse_mode = "HTML",
				disable_web_page_preview = True,
				reply_markup = Buttons
			)
			
	# Задаёт заголовок кнопки.
	def setButtonHeader(self, Header: str):
		# Запись заголовка кнопки.
		self.__Settings["button"] = Header
		# Сохранение настроек.
		self.__SaveSettings()
		
	# Задаёт ссылку кнопки.
	def setButtonLink(self, Link: str):
		# Запись ссылки кнопки.
		self.__Settings["link"] = Link
		# Сохранение настроек.
		self.__SaveSettings()
	
	# Задаёт тип ожидаемого сообщения.
	def setExpectedType(self, Type: ExpectedMessageTypes):
		self.__ExpectedType = Type