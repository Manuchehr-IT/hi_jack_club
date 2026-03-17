from enum import Enum

class SendMethod(str, Enum):
	TEXT = "sendMessage"
	PHOTO = "sendPhoto"
	VIDEO = "sendVideo"
	DOCUMENT = "sendDocument"
	AUDIO = "sendAudio"
	MEDIA_GROUP = "sendMediaGroup"
	# VOICE = "sendVoice"
	# LOCATION = "sendLocation"
	# CONTACT = "sendContact"
	# POLL = "sendPoll"
	# CHAT_ACTION = "sendChatAction"
