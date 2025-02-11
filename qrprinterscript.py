import qrcode
from PIL import Image, ImageDraw

# Parameters
num_qr = 24  # Number of QR codes
cols = 4  # Number of columns
rows = 6   # Number of rows (num_qr / cols)
qr_size = 300  # Size of each QR code in pixels

# Calculate canvas size (including margins)
dpi = 300  
canvas_width = 8.5 * dpi  
canvas_height = 11 * dpi  
canvas_size = (int(canvas_width), int(canvas_height))

# Create a blank canvas
canvas = Image.new("RGB", canvas_size, "white")
draw = ImageDraw.Draw(canvas)

first_x = 384+46
first_y = 337+46

between_x = 534+4
between_y = 515+20
num_so_far = 0

current_x = first_x
current_y = first_y
# Generate and place QR codes
for i in range(num_qr):
    if num_so_far % cols == 0 and num_so_far != 0:
        current_x = first_x
        current_y += between_y
    num_so_far += 1
    data = f"QR Code {i+1}"  # Unique data for each QR code
    qr = qrcode.QRCode(box_size=5, border=0)  # Adjust size
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill="black", back_color="white").resize((qr_size, qr_size))

    # Compute position with margins
    

    # Paste QR code on canvas
    canvas.paste(qr_img, (current_x-150, current_y-150))
    current_x += between_x
    #put a dot at 384, 337
    draw.ellipse((first_x-5, first_y-5, first_x+5, first_y+5), fill="red")

# trim the right side of the image
canvas = canvas.crop((0, 0, canvas_width, canvas_height))
# set image size to 9*11 inches
canvas = canvas.resize((int(9*300), int(11*300)))
# convert to pdf
canvas.save("qr_codes_page.pdf")# Show the canvas


# canvas.show()
