from Source.Functions import CreateExceptionMessage
from dublib.Methods.JSON import WriteJSON
from dublib.Polyglot import HTML
from threading import Thread
from telebot import types
from time import sleep

import telebot
import enum
import os

class ExpectedMessageTypes(enum.Enum):
	
	#---> Статические свойства.
	#==========================================================================================#
	Undefined = "undefined"
	Message = "message"
	Button = "button"
	Image = "image"
	Link = "link"

class BotManager:
	
	def __AutoApprover(self):
		Index = 0
		
		while True:
			
			if len(self.__Requests) > 0:
				Bufer = self.__Requests[0]
				ChatID = list(Bufer.keys())[0]
				UserChatID = Bufer[ChatID]
				
				try:
					self.__Bot.approve_chat_join_request(ChatID, UserChatID)
					
				except Exception as ExceptionData:
					if self.__Settings["report"] != None: self.__Bot.send_message(
						chat_id = self.__Settings["report"],
						text = CreateExceptionMessage("approve_chat_join_request", ExceptionData, {"ChatID": ChatID, "UserChatID": UserChatID}),
						parse_mode = "MarkdownV2"
					)
					
					if Index == 2:
						self.__Requests.pop(0)
						Index = 0
						
					Index += 1
				
				else:
					self.__Requests.pop(0)
					Index = 0
					
				sleep(1)
	
	def __SaveSettings(self):
		WriteJSON("Settings.json", self.__Settings)
	
	def __Supervisor(self):
		
		while True:
			sleep(60)

			if self.__AutoApproverThread.is_alive() == False:
				self.__AutoApproverThread = Thread(target = self.__AutoApprover, name = "Auto approver.")
				self.__AutoApproverThread.start()

	def __init__(self, Settings: dict, Bot: telebot.TeleBot):
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__AutoApproverThread = Thread(target = self.__AutoApprover, name = "Auto approver thread.")
		self.__SupervisorThread = Thread(target = self.__Supervisor, name = "Supervisor thread.")
		self.__ExpectedType = ExpectedMessageTypes.Undefined
		self.__Settings = Settings.copy()
		self.__Bot = Bot
		self.__Requests = list()
		
		self.__AutoApproverThread.start()
		if self.__Settings["use-supervisor"] == True: self.__SupervisorThread.start()
		
	def addRequest(self, Message: telebot.types.ChatJoinRequest):
		Bufer = dict()
		Bufer[Message.chat.id] = Message.user_chat_id
		self.__Requests.append(Bufer)
		
	def collect(self, Status: bool):
		self.__Settings["collect-media"] = Status
		self.__SaveSettings()
		
	def disable(self):
		self.__Settings["active"] = False
		self.__SaveSettings()
		
	def editMessage(self, Text: str) -> bool:
		IsCorrected = True
		MaxLength = 1024 if self.__Settings["premium"] == False else 2048
		if len(os.listdir("Data")) == 0: MaxLength = 4096 
		
		if len(HTML(Text).plain_text) >= MaxLength:
			self.disable()
			IsCorrected = False
			
		else:
			self.__Settings["message"] = Text
			self.__SaveSettings()
			
		return IsCorrected
		
	def enable(self):
		self.__Settings["active"] = True
		self.__SaveSettings()
		
	def getAttachmentsCount(self) -> int:
		Count = len(os.listdir("Data"))
		
		return Count
		
	def getData(self) -> dict:
		return self.__Settings.copy()

	def getExpectedType(self) -> ExpectedMessageTypes:
		return self.__ExpectedType
	
	def getStatus(self) -> bool:
		return self.__Settings["active"]
	
	def isCollect(self) -> bool:
		return self.__Settings["collect-media"]
	
	def login(self, UserID: int, Password: str | None = None) -> bool:
		IsAdmin = False

		if Password == None and UserID in self.__Settings["admins"]:
			IsAdmin = True
			
		return IsAdmin
	
	def register(self, UserID: int):
		self.__Settings["admins"].append(UserID)
		self.__SaveSettings()
		
	def removeButton(self):
		self.__Settings["button"] = None
		self.__Settings["link"] = None
		self.__SaveSettings()
		
	def sendHi(self, ChatID: int):
		Files = os.listdir("Data")[:10]
		Buttons = None
		
		if len(Files) > 0:
			Attachments = list()
			
			for Index in range(0, len(Files)):
				
				Attachments.append(
					types.InputMediaPhoto(
						open("Data/" + Files[Index], "rb"), 
						caption = self.__Settings["message"] if Index == 0 else "",
						parse_mode = "HTML"
					)
				)
				
			try:
				self.__Bot.send_media_group(
					ChatID,
					media = Attachments
				)
			except telebot.apihelper.ApiException: pass
			
		else:
			
			if self.__Settings["button"] != None and self.__Settings["link"] != None:
				Buttons = types.InlineKeyboardMarkup()
				Button = types.InlineKeyboardButton(self.__Settings["button"], self.__Settings["link"])
				Buttons.add(Button)

			if len(self.__Settings["message"]) > 0:
				try:
					self.__Bot.send_message(
						ChatID,
						text = self.__Settings["message"],
						parse_mode = "HTML",
						disable_web_page_preview = True,
						reply_markup = Buttons
					)
				except telebot.apihelper.ApiException: pass
			
	def setButtonHeader(self, Header: str):
		self.__Settings["button"] = Header
		self.__SaveSettings()
		
	def setButtonLink(self, Link: str):
		self.__Settings["link"] = Link
		self.__SaveSettings()
	
	def setExpectedType(self, Type: ExpectedMessageTypes):
		self.__ExpectedType = Type