#!/usr/bin/python

from dublib.Methods import CheckPythonMinimalVersion, MakeRootDirectories, ReadJSON, RemoveFolderContent
from urllib.parse import urlparse
from Source.BotManager import *
from Source.Functions import *
from telebot import types

import telebot

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ СКРИПТА <<<<< #
#==========================================================================================#

# Проверка поддержки используемой версии Python.
CheckPythonMinimalVersion(3, 10)
# Создание папок в корневой директории.
MakeRootDirectories(["Data"])

#==========================================================================================#
# >>>>> ЧТЕНИЕ НАСТРОЕК <<<<< #
#==========================================================================================#

# Чтение настроек.
Settings = ReadJSON("Settings.json")

# Если токен не указан, выбросить исключение.
if type(Settings["token"]) != str or Settings["token"].strip() == "":
	raise Exception("Invalid Telegram bot token.")

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ БОТА <<<<< #
#==========================================================================================#

# Токен для работы определенного бота телегамм.
Bot = telebot.TeleBot(Settings["token"])
# Менеджер данных бота.
BotProcessor = BotManager(Settings, Bot)

#==========================================================================================#
# >>>>> ОБРАБОТКА ЗАПРОСОВ <<<<< #
#==========================================================================================#
		
# Обработка команды: start.
@Bot.message_handler(commands=["start"])
def Command(Message: types.Message):
	# Описание авторизации.
	AuthorizationDescription = "*разрешён*"
	# Меню администратора.
	Menu = CreateMenu(BotProcessor)
	
	# Вход в бота.
	if BotProcessor.login(Message.from_user.id) == False:
		# Изменить описание входа.
		AuthorizationDescription = "*запрещён*"
		# Отключение разметки.
		Menu = types.ReplyKeyboardRemove()
		
	# Отправка сообщения: приветствие.
	Bot.send_message(
		Message.chat.id,
		"Здравствуйте\. Я бот, приветствующий новых участников нашего канала\.\n\n🔒 Доступ к функциям администрирования: " + AuthorizationDescription,
		parse_mode = "MarkdownV2",
		disable_web_page_preview = True,
		reply_markup = Menu
	)
	
# Обработка команды: debug.
@Bot.message_handler(commands=["debug"])
def Command(Message: types.Message):
	
	# Если пользователь уже администратор.
	if BotProcessor.login(Message.from_user.id) == True:
		# Получение данных.
		BotData = BotProcessor.getData()
		# Генерация отладочных параметров.
		Premium = "Premium: _*" + str(BotData["premium"]).lower() + "*_\n"
		MessageText = "Текст сообщения: " + EscapeCharacters(str(BotData["message"]) + "\n") if BotData["message"] != "" else "Текст сообщения: _*null*_\n"
		ButtonHeader = "Заголовок кнопки: " + EscapeCharacters(str(BotData["button"]) + "\n") if BotData["button"] != None else "Заголовок кнопки: _*null*_\n"
		ButtonLink = "Ссылка кнопки: _" + EscapeCharacters(str(BotData["link"]) + "_\n") if BotData["link"] != None else "Ссылка кнопки: _*null*_\n"
		IsCollect = "Коллекционирование: _*" + str(BotData["collect-media"]).lower() + "*_\n"
		# Список отладочных параметров.
		DebugInfo = [Premium, MessageText, ButtonHeader, ButtonLink, IsCollect]
		
		# Отправка сообщения: приветствие.
		Bot.send_message(
			Message.chat.id,
			"🐞 *Отладка*\n\n" + "".join(DebugInfo),
			parse_mode = "MarkdownV2",
			reply_markup = CreateMenu(BotProcessor)
		)

# Обработка команды: delbutton.
@Bot.message_handler(commands=["delbutton"])
def Command(Message: types.Message):
	
	# Если пользователь уже администратор.
	if BotProcessor.login(Message.from_user.id) == True:
		# Удаление кнопки.
		BotProcessor.removeButton()
		# Отправка сообщения: приветствие.
		Bot.send_message(
			Message.chat.id,
			"🕹️ *Изменение кнопки*\n\nКнопка отключена\.",
			parse_mode = "MarkdownV2",
			disable_web_page_preview = True,
			reply_markup = CreateMenu(BotProcessor)
		)
	
# Обработка команды: unattach.
@Bot.message_handler(commands=["unattach"])
def Command(Message: types.Message):
	
	# Если пользователь уже администратор.
	if BotProcessor.login(Message.from_user.id) == True:
		# Удаление текущих вложений.
		RemoveFolderContent("Data")
		# Установка ожидаемого типа сообщения.
		BotProcessor.setExpectedType(ExpectedMessageTypes.Undefined)
		# Отправка сообщения: приветствие.
		Bot.send_message(
			Message.chat.id,
			"🖼️ *Добавление вложений*\n\nВсе вложения удалены\.",
			parse_mode = "MarkdownV2",
			disable_web_page_preview = True,
			reply_markup = CreateMenu(BotProcessor)
		)
	
# Обработка текстовых сообщений.
@Bot.message_handler(content_types=["text"])
def TextMessage(Message: types.Message):
	
	# Реагирование на сообщение по ожидаемому типу.
	match BotProcessor.getExpectedType():
		
		# Тип сообщения – текст приветствия.
		case ExpectedMessageTypes.Message:
			# Сохранение нового текста.
			Result = BotProcessor.editMessage(Message.html_text)
			# Комментарий.			
			Comment = "Текст приветственного сообщения изменён\." if Result == True else EscapeCharacters("Сообщение слишком длинное! Telegram устанавливает следующие лимиты:\n\n4096 символов – обычное сообщение;\n2048 символов – сообщение с вложениями (Premium);\n1024 символа – сообщение с вложениями.")
			# Отправка сообщения: редактирование приветствия завершено.
			Bot.send_message(
				Message.chat.id,
				"✍ *Редактирование приветствия*\n\n" + Comment,
				parse_mode = "MarkdownV2",
				disable_web_page_preview = True,
				reply_markup = CreateMenu(BotProcessor)
			)
			# Установка ожидаемого типа сообщения.
			BotProcessor.setExpectedType(ExpectedMessageTypes.Undefined)
			
		# Тип сообщения – заголовок кнопки.
		case ExpectedMessageTypes.Button:
			# Если нет вложений.
			if BotProcessor.getAttachmentsCount() == 0:
				# Изменение заголовка кнопки.
				BotProcessor.setButtonHeader(Message.text)
				# Отправка сообщения: изменение заголовка кнопки.
				Bot.send_message(
					Message.chat.id,
					"🕹️ *Изменение кнопки*\n\nДля кнопки установлен следующий заголовок: _" + EscapeCharacters(Message.text) + "_\.",
					parse_mode = "MarkdownV2",
					disable_web_page_preview = True,
					reply_markup = CreateMenu(BotProcessor)
				)
				
			else:
				# Отправка сообщения: нельзя использовать кнопку вместе с вложениями.
				Bot.send_message(
					Message.chat.id,
					"🕹️ *Изменение кнопки*\n\nTelegram не позволяет добавлять кнопку в сообщения с вложениями\.",
					parse_mode = "MarkdownV2",
					disable_web_page_preview = True,
					reply_markup = CreateMenu(BotProcessor)
				)
				
			# Установка ожидаемого типа сообщения.
			BotProcessor.setExpectedType(ExpectedMessageTypes.Undefined)
			
		# Тип сообщения – заголовок кнопки.
		case ExpectedMessageTypes.Link:
			
			# Если нет вложений.
			if BotProcessor.getAttachmentsCount() == 0:

				# Если строка является URL.
				if bool(urlparse(Message.text).scheme) == True:
					# Изменение заголовка кнопки.
					BotProcessor.setButtonLink(Message.text)
					# Отправка сообщения: изменение заголовка кнопки.
					Bot.send_message(
						Message.chat.id,
						"🕹️ *Изменение кнопки*\n\nДля кнопки установлен следующий URL: _" + EscapeCharacters(Message.text) + "_\.",
						parse_mode = "MarkdownV2",
						disable_web_page_preview = True,
						reply_markup = CreateMenu(BotProcessor)
					)
					
				else:
					# Отправка сообщения: неверный URL.
					Bot.send_message(
						Message.chat.id,
						"🕹️ *Изменение кнопки*\n\nНе удалось расспознать ссылку\. Отправьте мне адрес ресурса в формате URL\.",
						parse_mode = "MarkdownV2",
						disable_web_page_preview = True,
						reply_markup = CreateMenu(BotProcessor)
					)
				
			else:
				# Отправка сообщения: нельзя использовать кнопку вместе с вложениями.
				Bot.send_message(
					Message.chat.id,
					"🕹️ *Изменение кнопки*\n\nTelegram не позволяет добавлять кнопку в сообщения с вложениями\.",
					parse_mode = "MarkdownV2",
					disable_web_page_preview = True,
					reply_markup = CreateMenu(BotProcessor)
				)
				
			# Установка ожидаемого типа сообщения.
			BotProcessor.setExpectedType(ExpectedMessageTypes.Undefined)
		
		# Тип сообщения – неопределённый или отключение коллекции.
		case ExpectedMessageTypes.Undefined | ExpectedMessageTypes.Image:
	
			# Если пользователь ввёл пароль администратора.
			if BotProcessor.login(Message.from_user.id) == False and Message.text == Settings["password"]:
				# Назначение пользователя администратором.
				BotProcessor.register(Message.from_user.id)
				# Отправка сообщения: выданы права администратора.
				Bot.send_message(
					Message.chat.id,
					"🔒 Доступ к функциям администрирования: *разрешён*",
					parse_mode = "MarkdownV2",
					disable_web_page_preview = True,
					reply_markup = CreateMenu(BotProcessor)
				)
				
			# Если пользователь уже администратор.
			if BotProcessor.login(Message.from_user.id) == True:
		
				# Обработка нажатий на кнопки меню.
				match Message.text:
		
					# Редактирование поста.
					case "✍ Редактировать":
						# Отправка сообщения: редактирование приветствия.
						Bot.send_message(
							Message.chat.id,
							"✍ *Редактирование приветствия*\n\nОтправьте мне текст вашего нового приветствия\.",
							parse_mode = "MarkdownV2",
							disable_web_page_preview = True,
							reply_markup = CreateMenu(BotProcessor)
						)
						# Установка ожидаемого типа сообщения.
						BotProcessor.setExpectedType(ExpectedMessageTypes.Message)
						
					# Добавление вложений.
					case "🖼️ Медиа":
						# Запуск коллекционирования.
						BotProcessor.collect(True)
						# Отправка сообщения: добавление вложений.
						Bot.send_message(
							Message.chat.id,
							"🖼️ *Добавление вложений*\n\nОтправляйте мне изображения, которые необходимо прикрепить к приветственному сообщению, или выполните команду /unattach для удаления всех вложений\.",
							parse_mode = "MarkdownV2",
							disable_web_page_preview = True,
							reply_markup = CreateMenu(BotProcessor)
						)
						# Установка ожидаемого типа сообщения.
						BotProcessor.setExpectedType(ExpectedMessageTypes.Image)
						
					# Добавление вложений.
					case "🖼️ Медиа (остановить)":
						# Запуск коллекционирования.
						BotProcessor.collect(False)
						# Количество вложений.
						AttachmentsCount = BotProcessor.getAttachmentsCount()
						# Отправка сообщения: добавление вложений.
						Bot.send_message(
							Message.chat.id,
							f"🖼️ *Добавление вложений*\n\nКоличество вложений: {AttachmentsCount}\.",
							parse_mode = "MarkdownV2",
							disable_web_page_preview = True,
							reply_markup = CreateMenu(BotProcessor)
						)
						# Установка ожидаемого типа сообщения.
						BotProcessor.setExpectedType(ExpectedMessageTypes.Undefined)
						
					# Изменение текста кнопки.
					case "🕹️ Кнопка":
						
						# Если нет вложений.
						if BotProcessor.getAttachmentsCount() == 0:
							# Отправка сообщения: изменение текста кнопки.
							Bot.send_message(
								Message.chat.id,
								"🕹️ *Изменение кнопки*\n\nОтправляйте мне название кнопки или выполните команду /delbutton для её отключения\.",
								parse_mode = "MarkdownV2",
								disable_web_page_preview = True,
								reply_markup = CreateMenu(BotProcessor)
							)
							# Установка ожидаемого типа сообщения.
							BotProcessor.setExpectedType(ExpectedMessageTypes.Button)
				
						else:
							# Отправка сообщения: нельзя использовать кнопку вместе с вложениями.
							Bot.send_message(
								Message.chat.id,
								"🕹️ *Изменение кнопки*\n\nTelegram не позволяет добавлять кнопку в сообщения с вложениями\.",
								parse_mode = "MarkdownV2",
								disable_web_page_preview = True,
								reply_markup = CreateMenu(BotProcessor)
							)	
						
					# Изменение ссылки кнопки.
					case "🔗 URL":
						
						# Если нет вложений.
						if BotProcessor.getAttachmentsCount() == 0:
							# Отправка сообщения: изменение ссылки кнопки.
							Bot.send_message(
								Message.chat.id,
								"🕹️ *Изменение кнопки*\n\nОтправляйте мне URL для перехода по нажатию кнопки или выполните команду /delbutton для её отключения\.",
								parse_mode = "MarkdownV2",
								disable_web_page_preview = True,
								reply_markup = CreateMenu(BotProcessor)
							)
							# Установка ожидаемого типа сообщения.
							BotProcessor.setExpectedType(ExpectedMessageTypes.Link)
							
						else:
							# Отправка сообщения: нельзя использовать кнопку вместе с вложениями.
							Bot.send_message(
								Message.chat.id,
								"🕹️ *Изменение кнопки*\n\nTelegram не позволяет добавлять кнопку в сообщения с вложениями\.",
								parse_mode = "MarkdownV2",
								disable_web_page_preview = True,
								reply_markup = CreateMenu(BotProcessor)
							)	
						
					# Предпросмотр сообщения.
					case "🔍 Предпросмотр":
						# Отправка сообщения: предпросмотр приветствия.
						BotProcessor.sendHi(Message.chat.id)
						
					# Остановка бота.
					case "🔴 Остановить":
						# Остановка бота.
						BotProcessor.disable()
						# Отправка сообщения: добавление вложений.
						Bot.send_message(
							Message.chat.id,
							"📢 *Техническая информация*\n\nРассылка приветственных сообщений остановлена\.",
							parse_mode = "MarkdownV2",
							disable_web_page_preview = True,
							reply_markup = CreateMenu(BotProcessor)
						)
						
					# Возобновление работы бота.
					case "🟢 Возобновить":
						# Возобновление работы бота.
						BotProcessor.enable()
						# Отправка сообщения: добавление вложений.
						Bot.send_message(
							Message.chat.id,
							"📢 *Техническая информация*\n\nРассылка приветственных сообщений возобновлена\.",
							parse_mode = "MarkdownV2",
							disable_web_page_preview = True,
							reply_markup = CreateMenu(BotProcessor)
						)
						
# Обработка изображений (со сжатием).					
@Bot.message_handler(content_types=["photo"])
def MediaAttachments(Message: types.Message):
	
	# Реагирование на сообщение по ожидаемому типу.
	match BotProcessor.getExpectedType():
		
		# Тип сообщения – текст приветствия.
		case ExpectedMessageTypes.Image:
			# Сохранение изображения.
			DownloadImage(Settings["token"], Bot, Message.photo[-1].file_id)
			# Установка ожидаемого типа сообщения.
			BotProcessor.setExpectedType(ExpectedMessageTypes.Undefined) 

# Обработка изображений (без сжатия).					
@Bot.message_handler(content_types=["document"])
def MediaAttachments(Message: types.Message):
	
	# Реагирование на сообщение по ожидаемому типу.
	match BotProcessor.getExpectedType():
		
		# Тип сообщения – текст приветствия.
		case ExpectedMessageTypes.Image:
			# Сохранение изображения.
			DownloadImage(Settings["token"], Bot, Message.document.file_id)
			# Установка ожидаемого типа сообщения.
			BotProcessor.setExpectedType(ExpectedMessageTypes.Undefined)
			
# Обработка заявок на вступление в канал.
@Bot.chat_join_request_handler()
def ProcessChatJoin(Message: telebot.types.ChatJoinRequest):
	# Отправка сообщения: приветствия.
	if BotProcessor.getStatus() == True: BotProcessor.sendHi(Message.from_user.id)
	# Помещение заявки в очередь на одобрение.
	if Settings["auto-approve"] == True: BotProcessor.addRequest(Message)

# Запуск обработки запросов Telegram.
Bot.infinity_polling(allowed_updates = telebot.util.update_types)