import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor, lightgrey
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image as PlatypusImage
from PIL import Image   
from gradio_client import Client

from google import genai
from google.genai import types

import os
HF_TOKEN = os.environ['HF_TOKEN']
GEMINI_API = os.environ['GEMINI_API']



# from dotenv import load_dotenv
# load_dotenv()  # Load from .env file

import sys
import io
# Fix encoding for all platforms
if sys.stdout.encoding != 'UTF-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'UTF-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# client = Client("Qwen/Qwen2.5-Max-Demo",hf_token=HF_TOKEN)
client = genai.Client(api_key=GEMINI_API)

def generateSummaryUsingModel(data):
    # result = client.predict(
		# query=f"Generate a summary (minimum 250 words) in a paragraph on the basis of the provided event report inputs :\n{data}",
	# 	api_name="/model_chat"
    # )
    # formatted_result = result[1][0][1]
    
    
    query=f"Generate a summary (minimum 250 words) in a paragraph on the basis of the provided event report inputs :\n{data}",
    response = client.models.generate_content(
    # model="gemini-2.0-flash-lite-preview-02-05",
    model="gemini-2.0-flash",
    contents=query)
    # print(response.text)
    
    
    
    
    return response.text

def generate_pdf(data, output_filename="output.pdf"):
    c = canvas.Canvas(output_filename, pagesize=letter)
    page_width, page_height = letter
    margin_top = 72  # 1 inch from top
    margin_bottom = 36  # 0.5 inches from bottom
    current_page = 1

    # --- Custom Header ---
    def draw_header():
        # Logo on the right
        try:
            logo = ImageReader("logo.png")
            logo_width, logo_height = 200, 75
            c.drawImage(logo, page_width - 50 - logo_width, page_height - margin_top - 20, width=logo_width, height=logo_height)
            
            # Department text below logo
            dept_text = "Dept. of Computer Science - Bangalore Yeshwanthpur Campus"
            c.setFont("Helvetica", 8)
            c.drawRightString(page_width - 70, page_height - margin_top - 20, dept_text)
        except:
            pass

        # Left side content
        c.setFont("Helvetica-Bold", 12)
        c.drawString(120, page_height - margin_top - 20, "Event / Activity Report")

        # Activity and Date inputs
        c.setFont("Helvetica", 12)
        y_position = page_height - margin_top - 50
        c.drawString(50, y_position, f"Activity: {data['header']['activityName']}")
        c.drawString(50, y_position - 20, f"Date(s): {data['header']['activityDate']}")

        # Horizontal line
        c.setStrokeColor(HexColor("#4472c4"))
        c.line(50, y_position - 28, page_width - 50, y_position - 28)

    # --- Footer ---
    def draw_footer():
        c.setFont("Helvetica", 12)
        c.setFillColor(HexColor("#0"))
        c.drawString(50, margin_bottom + 10, "   # CS_BYC")
        c.drawRightString(page_width - 110, margin_bottom + 10, f"{current_page}")
        c.setStrokeColor(HexColor("#4472c4"))
        c.line(50, margin_bottom + 25, page_width - 50, margin_bottom + 25)

# this version has worked correctly
    def create_table(heading, data, y_start):
        styles = getSampleStyleSheet()
        styles["Normal"].fontName = "Helvetica"
        styles["Normal"].fontSize = 10
        styles["Normal"].leading = 12
        
        heading_style = styles["Normal"]
        heading_style.textColor = "white"

        # Original table data with header and all rows (including summary)
        table_data = [[Paragraph(f"<b>{heading}</b>", heading_style), ""]]
        heading_style.textColor = HexColor("#000000")
        
        for label, value in data:
            wrapped_label = Paragraph(f"<b>{label}</b>", styles["Normal"])
            if isinstance(value, PlatypusImage):
                wrapped_value = value
            else:
                processed_text = str(value).replace('\n', '<br/>')
                wrapped_value = Paragraph(processed_text, styles["Normal"])
            table_data.append([wrapped_label, wrapped_value])

        style = TableStyle([
            ('SPAN', (0,0), (1,0)),
            ('BACKGROUND', (0,0), (-1,0), HexColor("#002147")),
            ('TEXTCOLOR', (0,0), (-1,0), HexColor("#FFFFFF")),
            ('BACKGROUND', (0,1), (0,-1), lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, HexColor("#171616")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ])

        # Create and split initial table
        table = Table(table_data, colWidths=[150, 350])
        table.setStyle(style)

        avail_width = 500
        split_tables = []
        remaining_table = table
        
        while remaining_table:
            available_height = y_start - margin_bottom - 30
            parts = remaining_table.split(avail_width, available_height)
            if not parts:
                break
            split_tables.append(parts[0])
            remaining_table = parts[1] if len(parts) > 1 else None

        # Process splits to add headers while preserving all rows
        final_tables = []
        for i, tbl in enumerate(split_tables):
            if i == 0:
                # First table keeps original header
                final_tables.append(tbl)
            else:
                # Subsequent tables: new header + all rows from split
                # Preserve existing rows including summary
                new_data = [table_data[0]] + tbl._cellvalues
                new_table = Table(new_data, colWidths=[150, 350])
                new_table.setStyle(style)
                final_tables.append(new_table)

        # Drawing logic remains the same
        current_y = y_start
        for tbl in final_tables:
            tbl.wrapOn(c, avail_width, page_height)
            tbl_height = tbl._height

            if (current_y - tbl_height) < margin_bottom:
                c.showPage()
                nonlocal current_page
                current_page += 1
                draw_header()
                draw_footer()
                current_y = page_height - margin_top - 100

            tbl.drawOn(c, 50, current_y - tbl_height + 10)
            current_y -= tbl_height + 10

        return current_y
    
    
    # --- HOD Section ---
    def add_hod_section(y_position):
        nonlocal current_page
        hod_signature = data.get('files', {}).get('signatures', {}).get('hod', '')
        hod_text=None
        try : 
            if (data["signatures"]["hodText"]):
                hod_text = data["signatures"]["hodText"]
        except :
            hod_text = None
        # Calculate space needed (conservative estimate including image)
        max_image_height = 100  # Assuming max height for space check
        required_space = 30 + 10 + max_image_height + 20 + 40  # line + spacing + image + text spacing + text

       
        
        right_margin = page_width - 50
        if hod_text and not hod_signature:
                # Check page space
                if (y_position - required_space + max_image_height) < margin_bottom:
                    c.showPage()
                    current_page += 1
                    draw_header()
                    draw_footer()
                    y_position = page_height - margin_top - 100 + 15
                text_y = y_position
                c.setFont("Helvetica-Bold",15)
                c.drawRightString(right_margin,text_y,hod_text)
                c.setFont("Helvetica-Bold", 12)
                c.drawRightString(right_margin, text_y - 20, "Head of the Department")
                c.setFont("Helvetica", 12)
                c.drawRightString(right_margin, text_y - 40, "(Vinay M)")

        try:
            
            if hod_signature :
                # Check page space
                extra_y = 5
                if (y_position - required_space + 50) < margin_bottom:
                    c.showPage()
                    current_page += 1
                    draw_header()
                    draw_footer()
                    y_position = page_height - margin_top - 90
                    # extra_y = 20
                img = Image.open(hod_signature)
                img_w, img_h = img.size
                aspect = img_w / img_h
                max_w = 100
                scaled_w = min(max_w, img_w)
                scaled_h = scaled_w / aspect

                # Position calculations
                right_margin = page_width - 50
                image_x = right_margin - scaled_w
                image_y = y_position - scaled_h + extra_y

                # Draw image
                c.drawImage(hod_signature, image_x, image_y, width=scaled_w, height=scaled_h)

                # Draw text
                text_y = image_y - 20
                c.setFont("Helvetica-Bold", 12)
                c.drawRightString(right_margin, text_y, "Head of the Department")
                c.setFont("Helvetica", 12)
                c.drawRightString(right_margin, text_y - 20, "(Vinay M)")

            return text_y - 40
        except:
            return y_position

    # version 2 of add_annexure : 
    def add_annexure(y_position):
        nonlocal current_page
        page_content_height = page_height - margin_top - margin_bottom - 100  # Available space between header and footer
        y_position -= 1
        if y_position < margin_bottom + 220:
            c.showPage()
            current_page += 1
            draw_header()
            draw_footer()
            y_position = page_height - margin_top - 100 - 5
        c.setFont("Helvetica-Bold", 13)
        c.drawString(50, y_position, "Annexure")
        y_position -= 20
        annex_data = data.get('files', {}).get('annexure', {})
        speaker_profile_text = data.get('speakerProfile', {}).get('text', '')
        speaker_profile_images = data.get('files', {}).get('speaker_profile', {}).get('speakerProfile', '')
        
        # Handle Speaker Profile
        if speaker_profile_text or speaker_profile_images:
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y_position, "1. Speaker Profile")
            y_position -= 20

            if speaker_profile_text:
                c.setFont("Helvetica", 10)
                text_lines = speaker_profile_text.split('\n')
                for line in text_lines:
                    if y_position < margin_bottom + 30:
                        c.showPage()
                        current_page += 1
                        draw_header()
                        draw_footer()
                        y_position = page_height - margin_top - 100
                    
                    text_object = c.beginText(50, y_position)
                    text_object.setFont("Helvetica", 10)
                    text_object.setTextOrigin(50, y_position)
                    max_width = page_width - 100
                    wrapped_text = wrap_text(line, max_width, c)
                    text_object.textLines(wrapped_text)
                    c.drawText(text_object)
                    y_position -= len(wrapped_text) * 12
                y_position -= 20

            if speaker_profile_images:
                x_pos = 50
                max_width = 250
                row_height = 0
                try:
                    img = Image.open(speaker_profile_images)
                    img_w, img_h = img.size
                    aspect = img_w / img_h
                    scaled_w = min(max_width, img_w)
                    scaled_h = scaled_w / aspect

                    if x_pos + scaled_w > page_width - 50:
                        x_pos = 50
                        y_position -= row_height + 15
                        row_height = 0

                    if y_position - scaled_h < margin_bottom:
                        c.showPage()
                        current_page += 1
                        draw_header()
                        draw_footer()
                        y_position = page_height - margin_top - 100
                        x_pos = 50
                        row_height = 0

                    c.drawImage(speaker_profile_images, x_pos, y_position - scaled_h, width=scaled_w, height=scaled_h)
                    x_pos += scaled_w + 15
                    row_height = max(row_height, scaled_h)
                except:
                    pass
                y_position -= row_height + 30
                
        # Define section layout configurations
        section_config = {
            'activity_photos': {'max_height': page_content_height, 'heading': "2. Photos of the activity"},
            'attendance': {'max_height': page_content_height, 'heading': "3. Attendance of participants"},
            'brochure_poster': {'max_height': page_content_height, 'heading': "4. Brochure/Poster"},
            'website_screenshots': {'max_height': page_content_height, 'heading': "5. Website Screenshots"},
            'student_feedback': {'max_height': page_content_height / 2, 'heading': "6. Student Feedback"},
        }

        for field, config in section_config.items():
            images = annex_data.get(field, [])
            if not images:
                continue

            # Check page space for heading
            if y_position < margin_bottom + 350 or ((config["heading"] == '2. Photos of the activity') and (y_position <  margin_bottom + 500)):
                c.showPage()
                current_page += 1
                draw_header()
                draw_footer()
                y_position = page_height - margin_top - 100 - 5

            # Add heading
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y_position, config['heading'])
            y_position -= 10  # Space after heading

            if config["heading"] == "2. Photos of the activity":

                    
                max_available_height = (y_position - margin_bottom - 60) / 2  # Divide space for two photos
                count = 1
                for img_path in images:
                    if ((y_position <  margin_bottom + 500) and count%2 != 0):
                        c.showPage()
                        current_page += 1
                        draw_header()
                        draw_footer()
                        y_position = page_height - margin_top - 95
                        c.setFont("Helvetica-Bold", 11)
                        c.drawString(50, y_position, config['heading'])
                        y_position -= 10  # Space after heading
                    try:
                        img = Image.open(img_path)
                        img_w, img_h = img.size
                        aspect = img_w / img_h

                        # Calculate height for two photos
                        target_height = min(config['max_height'] / 2, max_available_height)  # Half the max height for each photo

                        # Calculate width based on target height
                        scaled_h = min(target_height, img_h)
                        scaled_w = scaled_h * aspect

                        # Ensure width doesn't exceed page width
                        if scaled_w > (page_width - 100):
                            scaled_w = page_width - 100
                            scaled_h = scaled_w / aspect

                        # Center image horizontally
                        x_pos = 50

                        # Draw image
                        c.drawImage(img_path, x_pos, y_position - scaled_h, width=scaled_w, height=scaled_h)
                        count+=1
                        # Update position for the next photo
                        y_position -= scaled_h + 15  # 25px spacing after image

                    except Exception as e:
                        print(f"Error loading image {img_path}: {str(e)}")
                        continue
            else:
                for img_path in images:
                    try:
                        img = Image.open(img_path)
                        img_w, img_h = img.size
                        aspect = img_w / img_h
                        
                        # Calculate maximum available height
                        max_available_height = y_position - margin_bottom - 30  # 50px buffer
                        if (max_available_height < margin_bottom - 200 or (y_position < margin_bottom + 200)):
                                c.showPage()
                                current_page += 1
                                draw_header()
                                draw_footer()
                                y_position = page_height - margin_top - 100
                                
                                c.setFont("Helvetica-Bold", 11)
                                c.drawString(50, y_position, config['heading'])
                                y_position -= 5
                                
                                max_available_height = y_position - margin_bottom - 10
                        target_height = min(config['max_height'], max_available_height)
                        
                        # Calculate width based on target height
                        scaled_h = min(target_height, img_h)
                        scaled_w = scaled_h * aspect
                        
                        # Ensure width doesn't exceed page width
                        if scaled_w > (page_width - 100):
                            scaled_w = page_width - 100
                            scaled_h = scaled_w / aspect
                            scaled_h = min(scaled_h, config['max_height'])

                        if (config['heading'] != '3. Attendance of participants') and (config['heading'] != '6. Student Feedback') and (config["heading"] != '2. Photos of the activity') and (config['heading'] != '5. Website Screenshots') :
                            # Check if image fits vertically
                            if scaled_h > (y_position - margin_bottom - 100): # changing
                                # Need to reduce height to fit
                                scaled_h = y_position - margin_bottom - 50
                                scaled_w = scaled_h * aspect
                                
                        
                        elif (config['heading'] == '6. Student Feedback'):
                            # Check if image fits vertically
                            if scaled_h > ((y_position - margin_bottom - 10)/2) and y_position < page_content_height/2 - margin_bottom - margin_top: # changing
                                # Need to reduce height to fit
                                scaled_h = (y_position - margin_bottom - 10)/2
                                scaled_w = scaled_h * aspect
                                
                        elif (config["heading"] == '2. Photos of the activity'):
                            # Check if image fits vertically
                            # scaled_h-=20
                            # if (y_position - scaled_h) < margin_bottom:
                            #     c.showPage()
                            #     current_page += 1
                            #     draw_header()
                            #     draw_footer()
                            #     y_position = page_height - margin_top - 100
                            #     scaled_h = min(config['max_height'], y_position - margin_bottom - 50 - 200)
                            #     scaled_w = scaled_h * aspect
                            #     c.setFont("Helvetica-Bold", 11)
                            #     c.drawString(50, y_position, config['heading'])
                            #     y_position -= 5
                            # if (y_position < page_height - margin_top - 200):
                            #     c.showPage()
                            #     current_page+=1
                            #     draw_header()
                            #     draw_footer()
                            #     y_position = page_content_height - margin_top - 100
                            #     c.setFont("Helvetica-Bold", 11)
                            #     c.drawString(50, y_position, config['heading'])
                            #     y_position -= 5
                            pass

                            
                        
                        else:
                            # Check if image fits vertically
                            if scaled_h > (y_position - margin_bottom - 100) and y_position > 300: # changing
                                # Need to reduce height to fit
                                scaled_h = y_position - margin_bottom - 50
                                scaled_w = scaled_h * aspect

                        # Check if we need a new page
                        if (y_position - scaled_h) < margin_bottom + 50 and config["heading"]!='2. Photos of the activity':
                            c.showPage()
                            current_page += 1
                            draw_header()
                            draw_footer()
                            y_position = page_height - margin_top - 100
                            scaled_h = min(config['max_height'], y_position - margin_bottom - 50)
                            scaled_w = scaled_h * aspect
                            if scaled_w > (page_width - 100):
                                scaled_w = page_width - 100
                                scaled_h = scaled_w / aspect
                            c.setFont("Helvetica-Bold", 11)
                            c.drawString(50, y_position, config['heading'])
                            y_position -= 5


                        # Center image horizontally
                        x_pos = (page_width - scaled_w) / 2 if config['max_height'] == page_content_height and config["heading"]!='2. Photos of the activity' else 50
                        
                        # for centering studend feedback section
                        x_pos = (page_width - scaled_w) / 2 if config['heading'] == '6. Student Feedback' else 50
                        # Draw image
                        # if (config["heading"] != '2. Photos of the activity'):
                        c.drawImage(img_path, x_pos, y_position - scaled_h, width=scaled_w, height=scaled_h)
                        # Update position
                        y_position -= scaled_h + 25  # 30px spacing after image

                    except Exception as e:
                        print(f"Error loading image {img_path}: {str(e)}")
                        continue
            
        action_taken_report_text = data.get('actionTakenReport', {}).get('text', '')
        action_taken_report_images = annex_data.get('action_taken_report', [])
        # Existing code for other sections...
        # Handle Action Taken Report
        if action_taken_report_text or action_taken_report_images:
            if y_position < margin_bottom + 200:
                c.showPage()
                current_page += 1
                draw_header()
                draw_footer()
                y_position = page_height - margin_top - 100 - 18
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y_position, "7. Action Taken Report")
            y_position -= 20

            # Handle Text
            if action_taken_report_text:
                c.setFont("Helvetica", 10)
                text_lines = action_taken_report_text.split('\n')
                for line in text_lines:
                    if y_position < margin_bottom + 100:
                        c.showPage()
                        current_page += 1
                        draw_header()
                        draw_footer()
                        y_position = page_height - margin_top - 100 - 18
                    # Create TextObject and set its width for wrapping
                    text_object = c.beginText(50, y_position)
                    text_object.setFont("Helvetica", 10)
                    text_object.setTextOrigin(50, y_position)

                    # Add the wrapped text using the textObject
                    max_width = page_width - 100  # Adjust the width for the margin
                    wrapped_text = wrap_text(line, max_width, c)
                    text_object.textLines(wrapped_text)
                    c.drawText(text_object)
                    y_position -= len(wrapped_text) * 12  # Adjust line height dynamically
                y_position -= 20

            # Handle Images
            if action_taken_report_images:
                x_pos = 50
                max_width = 150
                row_height = 0

                for img_path in action_taken_report_images:
                    try:
                        img = Image.open(img_path)
                        img_w, img_h = img.size
                        aspect = img_w / img_h
                        scaled_w = min(max_width, img_w)
                        scaled_h = scaled_w / aspect

                        if x_pos + scaled_w > page_width - 50:
                            x_pos = 50
                            y_position -= row_height + 15
                            row_height = 0

                        if y_position - scaled_h < margin_bottom:
                            c.showPage()
                            current_page += 1
                            draw_header()
                            draw_footer()
                            y_position = page_height - margin_top - 100
                            x_pos = 50
                            row_height = 0

                        c.drawImage(img_path, x_pos, y_position - scaled_h, width=scaled_w, height=scaled_h)
                        x_pos += scaled_w + 15
                        row_height = max(row_height, scaled_h)
                    except:
                        continue

                y_position -= row_height + 30
        
        return y_position

    
    def wrap_text(text, max_width, canvas):
        """
        Wrap the text to fit within the specified max_width of the canvas.
        """
        words = text.split(' ')
        wrapped_lines = []
        current_line = ''

        for word in words:
            # Check if adding the word exceeds max width
            if canvas.stringWidth(current_line + ' ' + word) <= max_width:
                if current_line:
                    current_line += ' ' + word
                else:
                    current_line = word
            else:
                wrapped_lines.append(current_line)
                current_line = word

        # Add the last line
        if current_line:
            wrapped_lines.append(current_line)

        return wrapped_lines
    
    
    # --- Main Content Flow ---
    def add_content():
        nonlocal current_page
        y_pos = page_height - margin_top - 95
        
        # Activity Report Title
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(page_width/2, y_pos, "Activity Report")
        y_pos -= 20

        # Main Tables
        tables = [
            ("General Information", [
                ("Type of Activity:", data["generalInfo"]["type"]),
                ("Title of Activity:", data["generalInfo"]["title"]),
                ("Time:", data["generalInfo"]["time"]),
                ("Venue:", data["generalInfo"]["venue"]),
                ("Collaboration/Sponsor:", data["generalInfo"]["collaboration"]),
                ("SDGs Linked:", data["generalInfo"]["sdgs"]),
                ("Website/Platform:", data["generalInfo"]["website"]),
                ("Video Links:", data["generalInfo"]["videos"])
            ]),
            ("Speaker Details", [
                ("Name:", data["speaker"]["name"]),
                ("Title/Position:", data["speaker"]["title"]),
                ("Organization:", data["speaker"]["organization"]),
                ("Presentation Title:", data["speaker"]["presentation"])
            ]),
            ("Participants Profile", [
                ("Type of Participants:", data["participants"]["type"]),
                ("Total Participants:", data["participants"]["total"]),
                ("CHRIST Students:", data["participants"]["christStudents"]),
                ("CHRIST Faculty:", data["participants"]["christFaculty"]),
                ("Other Students:", data["participants"]["otherStudents"]),
                ("Other Faculty/Participants:", data["participants"]["otherFaculty"])
            ]),
            ("Synopsis", [
                ("Highlights:", data["synopsis"]["highlights"]),
                ("Key Takeaways:", data["synopsis"]["takeaways"]),
                ("Summary:", data["synopsis"]["summary"]),
                ("Follow-up Plan:", data["synopsis"]["followup"])
            ])
        ]
        report_prepared_rows = [
            ("Name of Organiser:", data["reportPrepared"]["name"]),
            ("Designation/Title:", data["reportPrepared"]["designation"]),
        ]
        # Handle signature type
        organizer_signature = data.get('files', {}).get('signatures', {}).get('organizer')
        if organizer_signature:
            try:
                img = PlatypusImage(organizer_signature, width=160, height=50)
                report_prepared_rows.append(("Signature:", img))
            except:
                report_prepared_rows.append(("Signature:", "Signature Image Error"))
        else:
            text_signature = data["reportPrepared"].get("signature", "")
            report_prepared_rows.append(("Signature:", text_signature))

        tables.append(("Report Prepared By", report_prepared_rows))

        for heading, rows in tables:
            y_pos = create_table(heading, rows, y_pos)
            if y_pos < margin_bottom + 200:
                c.showPage()
                current_page += 1
                draw_header()
                draw_footer()
                y_pos = page_height - margin_top - 100

        # Add HOD section
        y_pos = add_hod_section(y_pos)

        # Add annexure
        y_pos = add_annexure(y_pos)
        
        # Add HOD section again
        y_pos = add_hod_section(y_pos)

    

    # --- Execution ---
    draw_header()
    draw_footer()
    add_content()
    c.save()

def generate_newsletter(data, output_filename="newsletter.pdf"):
    c = canvas.Canvas(output_filename, pagesize=letter)
    page_width, page_height = letter
    margin = 50
    current_y = page_height - margin
    
    try:
        # --- Title Section ---
        title = data['generalInfo']['title']
        c.setFont("Helvetica-Bold", 18)
        
        # Define text wrapping parameters
        max_width = page_width - 2 * margin  # Available width for text
        max_height = 100  # Maximum height for the title section
        line_height = 20  # Height of each line of text
        
        
        from reportlab.lib.utils import simpleSplit
        # Split the title into multiple lines if it's too long
        wrapped_title = simpleSplit(title, "Helvetica-Bold", 18, max_width)
        
        # Draw each line of the wrapped title
        for line in wrapped_title:
            if current_y < margin + max_height:  # Check if we're running out of space
                c.showPage()  # Create a new page
                current_y = page_height - margin  # Reset Y position
            
            x_center = page_width / 2
            c.drawCentredString(x_center, current_y, line)
            current_y -= line_height
        
        # Adjust Y position for the next section
        current_y -= 20  # Add some extra space after the title

        # --- Activity Photos ---
        photos = data['files']['annexure'].get('activity_photos', [])
        if photos:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(margin, current_y, "Event Photos")
            current_y -= 10
            
            # Only take first 2 images
            selected_photos = photos[:2]
            
            # Calculate dimensions
            img_gap = 10  # Minimal gap between images
            img_height = 200  # Fixed height
            
            # Calculate image width (full width minus gap and margins)
            available_width = page_width - 2 * (margin/2 + 30) - img_gap
            img_width = available_width / 2
            
            x_pos = margin  # Start at left margin
            for img_path in selected_photos:
                try:
                    img = ImageReader(img_path)
                    c.drawImage(img, x_pos, current_y - img_height, 
                            width=img_width, 
                            height=img_height,
                            preserveAspectRatio=True,
                            mask='auto')
                    x_pos += img_width + img_gap
                except Exception as e:
                    print(f"Error loading image: {str(e)}")
                    continue
            
            current_y -= img_height + 20  # Space after images

        # --- Synopsis Sections ---
        synopsis = data['synopsis']
        sections = [
            ("Highlights", synopsis['highlights']),
            ("Key Takeaways", synopsis['takeaways']),
            ("Summary", synopsis['summary'])
        ]

        styles = getSampleStyleSheet()
        styles["Normal"].fontName = "Helvetica"
        styles["Normal"].fontSize = 12
        styles["Normal"].leading = 14
        our_data = ""

        for heading, content in sections:
            # Draw Heading
            # c.setFont("Helvetica-Bold", 14)
            # c.drawString(margin, current_y, f"{heading}:")
            # current_y -= 25
            our_data+=heading

            # Draw Content
            # text = Paragraph(content, styles["Normal"])
            our_data+="\n"+content
            # text.wrap(page_width - 2*margin, page_height)
            # text.drawOn(c, margin, current_y - text.height)
            # current_y -= text.height + 30

        paragraph = generateSummaryUsingModel(our_data)
        # sample inputs
        # paragraph = """1) Understanding Breast Cancer: The seminar began with an overview of breast cancer, explaining its nature as a mass of uncontrollable cells that can develop in the lining of milk ducts. Risk factors, stages, and signs and symptoms were discussed, emphasizing the importance of Breast Self-Examination (BSE). 2) Naturopathy in Breast Cancer Treatment: Dr. Mahi Gupta elaborated on the principles of naturopathy, which focus on treating the whole person, identifying root causes, and embracing natural remedies. 3) Natural Healing Techniques: A variety of sustainable and holistic approaches were presented, including hydrotherapy, mud therapy, steam baths, herbal teas, oil massages, acupuncture, and yoga. Special attention was given to the benefits of antioxidants, probiotics, and specific practices like Nabhi Chikitsa and intermittent fasting."""
        text = Paragraph(paragraph,styles["Normal"])
        text.wrap(page_width - 2*margin, page_height)
        text.drawOn(c, margin, current_y - text.height)
        current_y -= text.height + 30
        # Page Break Check
        # if current_y < margin + 50:
        #     c.showPage()
        #     current_y = page_height - margin
        #     c.setFont("Helvetica", 12)  # Reset font after page break
            # c.drawString(50,current_y,our_data)

    finally:
        c.save()
        
if __name__ == "__main__":
    data = None
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
        
    action = data.get('action', 'report')
    print(f"and the format is : {format}")
    if action == 'newsletter':
        generate_newsletter(data, "newsletter.pdf")
    else :
        generate_pdf(data,"output.pdf")
    
    
    
