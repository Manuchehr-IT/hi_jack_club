import qrcode
from qrcode.constants import ERROR_CORRECT_H
from io import BytesIO

from django.core.files.base import ContentFile

def create_qr(user, data: str):
	qr = qrcode.QRCode(
		version=3,
		error_correction=ERROR_CORRECT_H,
		box_size=15,
		border=1,
	)

	qr.add_data(data)
	qr.make(fit=True)

	img = qr.make_image(
		fill_color="black",
		back_color="white"
	)

	buffer = BytesIO()
	img.save(buffer)
	buffer.seek(0)

	user.iiko_qr_code.save(f"{user.id}.png", ContentFile(buffer.getvalue()), save=True)
