from Source.Functions import CreateExceptionMessage
from dublib.Methods import WriteJSON
from dublib.Polyglot import HTML
from threading import Thread
from telebot import types
from time import sleep

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
	
	# Поток автоматического одобрения заявок.
	def __AutoApprover(self):
		# Индекс повтора.
		Index = 0
		
		# Постоянно.
		while True:
			
			# Если есть запросы.
			if len(self.__Requests) > 0:
				# Чтение первого в очереди запроса.
				Bufer = self.__Requests[0]
				# Получение данных.
				ChatID = list(Bufer.keys())[0]
				UserChatID = Bufer[ChatID]
				
				try:
					# Одобрение запроса.
					self.__Bot.approve_chat_join_request(ChatID, UserChatID)
					
				except Exception as ExceptionData:
					# Если указан чат для отправки отчётов, то отправить отчёт об ошибке.
					if self.__Settings["report"] != None: self.__Bot.send_message(
						chat_id = self.__Settings["report"],
						text = CreateExceptionMessage("approve_chat_join_request", ExceptionData, {"ChatID": ChatID, "UserChatID": UserChatID}),
						parse_mode = "MarkdownV2"
					)
					
					# Если это третий повтор.
					if Index == 2:
						# Удаление первого в очереди запроса.
						self.__Requests.pop(0)
						# Обнуление индекса повтора.
						Index = 0
						
					# Инкремент индекса.
					Index += 1
				
				else:
					# Удаление первого в очереди запроса.
					self.__Requests.pop(0)
					# Обнуление индекса повтора.
					Index = 0
					
				# Выжидание секунды.
				sleep(1)
	
	# Сохраняет настройки.
	def __SaveSettings(self):
		# Сохранение настроек.
		WriteJSON("Settings.json", self.__Settings)
	
	# Поток-надзиратель.
	def __Supervisor(self):
		
		# Постоянно.
		while True:
			# Выжидание минуты.
			sleep(60)

			# Если поток остановлен.
			if self.__AutoApproverThread.is_alive() == False:
				# Реинициализация потока.
				self.__AutoApproverThread = Thread(target = self.__AutoApprover, name = "Auto approver.")
				# Запуск потока.
				self.__AutoApproverThread.start()

	# Конструктор.
	def __init__(self, Settings: dict, Bot: telebot.TeleBot):
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Поток одобрения заявок.
		self.__AutoApproverThread = Thread(target = self.__AutoApprover, name = "Auto approver thread.")
		# Поток-надзиратель.
		self.__SupervisorThread = Thread(target = self.__Supervisor, name = "Supervisor thread.")
		# Текущий тип ожидаемого сообщения.
		self.__ExpectedType = ExpectedMessageTypes.Undefined
		# Глобальные настройки.
		self.__Settings = Settings.copy()
		# Экземпляр бота.
		self.__Bot = Bot
		# Очередь заявок на одобрение.
		self.__Requests = list()
		
		# Запуск потока автоматического одобрения заявок.
		self.__AutoApproverThread.start()
		# Если указано настройками, запустить поток-надзиратель.
		if self.__Settings["use-supervisor"] == True: self.__SupervisorThread.start()
		
	# Добавляет в очередь заявку на вступление.
	def addRequest(self, Message: telebot.types.ChatJoinRequest):
		# Буфер запроса.
		Bufer = dict()
		# Заполнение буфера.
		Bufer[Message.chat.id] = Message.user_chat_id
		# Добавление буфера в очередь.
		self.__Requests.append(Bufer)
		
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
	def editMessage(self, Text: str) -> bool:
		# Состояние: корректин ли текст.
		IsCorrected = True
		# Максимальная длина сообщения.
		MaxLength = 1024 if self.__Settings["premium"] == False else 2048
		if len(os.listdir("Data")) == 0: MaxLength = 4096 
		
		# Если сообщение слишком длинное.
		if len(HTML(Text).plain_text) >= MaxLength:
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
	def getData(self) -> dict:
		return self.__Settings.copy()

	# Возвращает тип ожидаемого сообщения.
	def getExpectedType(self) -> ExpectedMessageTypes:
		return self.__ExpectedType
	
	# Возвращает статус бота.
	def getStatus(self) -> bool:
		return self.__Settings["active"]
	
	# Возвращает состояние коллекционирования.
	def isCollect(self) -> bool:
		return self.__Settings["collect-media"]
	
	# Выполняет авторизацию администратора.
	def login(self, UserID: int, Password: str | None = None) -> bool:
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

			# Если сообщение не пустое.
			if len(self.__Settings["message"]) > 0:
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