#!/usr/bin/python3
import qrcode
import math
import sys
import os
import re
from io import BytesIO
from PIL import Image
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

def load_orga_vcards(filename, names):
	"""
	Load vCard data for organizers. limited info
	"""
	vcards = []

	if not os.path.exists(filename) or os.path.getsize(filename) == 0:
		print(f"Error: missing csv({filename})")
		sys.exit()

	with open(filename, 'r', encoding='utf-8') as file:
		vcards_data = file.read().strip().split('\n')

	# we have only first, last and email
	skip_first = 1
	for vcard in vcards_data:
		if skip_first:
			skip_first = 0
			continue
		line = vcard.split(',')
		names.append(line[0] + " " + line[1])
		vcard = """BEGIN:VCARD
VERSION:3.0
N:{}
FN:{}
ORG:{}
TITLE:{}
TEL;TYPE=WORK,VOICE:{}
ADR;TYPE=HOME:;;{}
EMAIL:{}
END:VCARD""".format( line[0] + " " + line[1], '', '', line[3], '', '', line[2])
		vcards.append(vcard)

	return vcards

def load_vcards(filename, names):
	"""
	Load vCard data from the specified file.
	"""
	vcards = []

	if not os.path.exists(filename) or os.path.getsize(filename) == 0:
		print(f"Error: missing csv({filename})")
		sys.exit()

	with open(filename, 'r') as file:
		vcards_data = file.read().strip().split('\n')  # Assuming each vCard is separated by a blank line

	skip_first = 1
	for vcard in vcards_data:
		if skip_first:
			skip_first = 0
			continue
		line = vcard.split(',')
		names.append(line[0] + " " + line[1])
		vcard = f"""BEGIN:VCARD
VERSION:3.0
N:%s
FN:%s
ORG:%s
TITLE:%s
TEL;TYPE=WORK,VOICE:%s
ADR;TYPE=HOME:;;%s
EMAIL:%s
END:VCARD""" % ( line[0] + ' ' + line[1], '', 'DevOpsDays 2024', '', '', '', line[2] )
		vcards.append(vcard)

	return vcards

def generate_qr_code(vcard):
	qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_L,
		box_size=10,
		border=4,
	)
	qr.add_data(vcard)
	qr.make(fit=True)
	img = qr.make_image(fill='black', back_color='white')
	# Save the QR code image to a BytesIO object
	img_buffer = BytesIO()
	img.save(img_buffer, format="PNG")
	img_buffer.seek(0)  # Reset buffer position to the beginning
	return ImageReader(img_buffer)

def generate_page(c, vcards, names):
	# Avery 5164 label dimensions and layout
	page_width, page_height = letter
	labels_per_row = 2
	labels_per_column = 3
	label_width = 4.0 * inch
	label_height = 3.33 * inch
	margin_x = 0.156 * inch
	margin_y = 0.5 * inch

	# For each page we need to set the font and size
	c.setFont(font_name, font_size)

	# Draw each label on the PDF
	for i, (vcard) in enumerate(vcards):
		col = i % labels_per_row
		row = i // labels_per_row
		
		if row >= labels_per_column:
		    break
		
		x = margin_x + col * (label_width + margin_x)
		y = page_height - margin_y - (row + 1) * label_height

		name_width = c.stringWidth(names[i], font_name, font_size)
		# Calculate the x-coordinate for centered text
		x_centered = x - name_width / 2 + label_width / 2
		
		# Draw name at the top
		c.drawString(x_centered, y + label_height - 60, names[i])
		
		# Center the QR code in the label
		qr_code_size = 2 * inch  # Size of the QR code
		qr_code_x = x + (label_width - qr_code_size) / 2
		qr_code_y = y + (label_height - qr_code_size) / 2 - 20  # Adjust the QR code position to leave space for the name

		qr_image = generate_qr_code(vcard)
		c.drawImage(qr_image, qr_code_x, qr_code_y, qr_code_size, qr_code_size)

def main(args):
	names = []
	vcards = []
	labels = []
	filename = ''
	args_num = len(args)

	if args_num == 0:
		print(f"Usage: {sys.argv[0]} orga|attendees")
		sys.exit()

	if len(args) == 1 and args[0] == 'orga':
		vcards = load_orga_vcards('organizers.csv', names)
		filename = 'orga.pdf'
	else:
		vcards = load_vcards('attendees.csv', names)
		filename = 'attendees.pdf'

	vcards_num = len(vcards)
	print(f"Found: %d vcards" % vcards_num)

	# Register the font.
	font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
	pdfmetrics.registerFont(TTFont(font_name, font_path))

	# Create a canvas to draw the PDF
	c = canvas.Canvas(filename, pagesize=letter)

	if vcards_num > 6:
		# Split vCards into chunks of 6 and create pages
		num_pages = math.ceil(len(vcards) / 6)
		for page_number in range(num_pages):
			start_index = page_number * 6
			end_index = start_index + 6
			vcard_chunk = vcards[start_index:end_index]
			name_chunk = names[start_index:end_index]
			# Generate each page
			for i, vcard in enumerate(vcard_chunk):
				generate_page(c, vcard_chunk, name_chunk)
			c.showPage()
	else:
		for i, vcard in enumerate(vcards):
			generate_page(c, vcards, names)
		c.showPage()
	
	c.save()
	print("Avery 5164 label PDF generated and saved as '{}'.".format(filename))

#font_name = "Arial"
font_name = "DejaVu"
font_size = 22

if __name__ == "__main__":
    main(sys.argv[1:])
