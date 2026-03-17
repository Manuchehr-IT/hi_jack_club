from aiogram.types import Message, InputMediaPhoto, InputMediaVideo
from typing import Dict, List

class MediaProcessing:
	@staticmethod
	def pack(media_files: List[Message | Dict], caption: str | None = None) -> List[InputMediaPhoto | InputMediaVideo]:
		media = [
			InputMediaPhoto(media=message.photo[-1].file_id)
			if message.photo else
			InputMediaVideo(media=message.video.file_id)
			for message in media_files
		] if isinstance(media_files[0], Message) else [
			InputMediaPhoto(media=media_file["file_id"])
			if media_file["type"] == "photo" else
			InputMediaVideo(media=media_file["file_id"])
			for media_file in media_files
		]

		if caption: media[0].caption = caption

		return media

	@staticmethod
	def parse_media_messages(messages: List[Message]):
		media = [
			{"type": "photo", "media": message.photo[-1].file_id}
			if message.photo else
			{"type": "video", "media": message.video.file_id}
			for message in messages
		]

		if media and messages[0].caption:
			media[0]["caption"] = messages[0].html_text
			media[0]["parse_mode"] = "HTML"

		return media
