import sys
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor, lightgrey
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image as PlatypusImage
from PIL import Image
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
        y_position = page_height - margin_top - 60
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

    # --- Table Creation ---
    def create_table(heading, data, y_start):
        styles = getSampleStyleSheet()
        styles["Normal"].fontName = "Helvetica"
        styles["Normal"].fontSize = 10
        styles["Normal"].leading = 12
        
        # Create a new style for the heading with white text
        heading_style = styles["Normal"]
        heading_style.textColor = HexColor("#000000")  # Set text color to white

        table_data = [[Paragraph(f"<b>{heading}</b>", heading_style), ""]]
        for label, value in data:
            wrapped_label = Paragraph(f"<b>{label}</b>", styles["Normal"])
            
            # Handle image or text signature
            if isinstance(value, PlatypusImage):
                wrapped_value = value
            else:
                wrapped_value = Paragraph(str(value), styles["Normal"])
            table_data.append([wrapped_label, wrapped_value])

        # Table styling
        style = TableStyle([
            ('SPAN', (0,0), (1,0)),
            ('BACKGROUND', (0,0), (-1,0), HexColor("#7399c9")),
            ('TEXTCOLOR', (0,0), (-1,0), HexColor("#FFFFFF")),
            ('BACKGROUND', (0,1), (0,-1), lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, HexColor("#171616")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ])

        table = Table(table_data, colWidths=[150, 350])
        table.setStyle(style)
        table.wrapOn(c, page_width, page_height)
        table_height = table._height

        # Page break check
        if (y_start - table_height) < margin_bottom + 200:
            c.showPage()
            nonlocal current_page
            current_page += 1
            draw_header()
            draw_footer()
            y_start = page_height - margin_top - 100

        # Draw table
        table.drawOn(c, 50, y_start - table_height)
        return y_start - table_height - 20

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

        # Check page space
        if (y_position - required_space) < margin_bottom:
            c.showPage()
            current_page += 1
            draw_header()
            draw_footer()
            y_position = page_height - margin_top - 100
        
        right_margin = page_width - 50
        if hod_text and not hod_signature:
                text_y = y_position - 15
                c.setFont("Helvetica-Bold",15)
                c.drawRightString(right_margin,text_y,hod_text)
                c.setFont("Helvetica-Bold", 12)
                c.drawRightString(right_margin, text_y - 20, "Head of the Department")
                c.setFont("Helvetica", 12)
                c.drawRightString(right_margin, text_y - 40, "(Vinay M)")

        try:
            
            if hod_signature : 
                img = Image.open(hod_signature)
                img_w, img_h = img.size
                aspect = img_w / img_h
                max_w = 100
                scaled_w = min(max_w, img_w)
                scaled_h = scaled_w / aspect

                # Position calculations
                right_margin = page_width - 50
                image_x = right_margin - scaled_w
                image_y = y_position - scaled_h - 20

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

    def add_annexure(y_position):
        nonlocal current_page
        y_position -= 20
        if y_position < margin_bottom + 220:
            c.showPage()
            current_page += 1
            draw_header()
            draw_footer()
            y_position = page_height - margin_top - 100 - 18

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

            # Handle Text
            if speaker_profile_text:
                c.setFont("Helvetica", 10)
                text_lines = speaker_profile_text.split('\n')

                # Handle wrapping and multiple lines
                for line in text_lines:
                    if y_position < margin_bottom + 50:
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
            if speaker_profile_images:
                x_pos = 50
                max_width = 150
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

    

        # Handle other sections (images only)
        sections = [
            ('activity_photos', "2. Photos of the activity"),
            ('attendance', "3. Attendance of participants"),
            ('brochure_poster', "4. Brochure/Poster"),
            ('website_screenshots', "5. Website Screenshots"),
            ('student_feedback', "6. Student Feedback"),
        ]

        for field, heading in sections:
            images = annex_data.get(field, [])
            if not images:
                continue

            # Check page space
            if y_position < margin_bottom + 220:
                c.showPage()
                current_page += 1
                draw_header()
                draw_footer()
                y_position = page_height - margin_top - 100 - 18

            # Add heading
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y_position, heading)
            y_position -= 10

            # Draw images in grid
            x_pos      = 50
            max_width  = 150
            row_height = 0
            
            for img_path in images:
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

                    if y_position - scaled_h < margin_bottom + 50:
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
                    if y_position < margin_bottom + 200:
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
        y_pos = page_height - margin_top - 105
        
        # Activity Report Title
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(page_width/2, y_pos, "Activity Report")
        y_pos -= 10

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
                img = PlatypusImage(organizer_signature, width=120, height=120)
                report_prepared_rows.append(("Signature:", img))
            except:
                report_prepared_rows.append(("Signature:", "Signature Image Error"))
        else:
            text_signature = data["reportPrepared"].get("signature", "")
            report_prepared_rows.append(("Signature:", text_signature))

        tables.append(("Report Prepared By", report_prepared_rows))

        for heading, rows in tables:
            y_pos = create_table(heading, rows, y_pos)
            if y_pos < margin_bottom + 100:
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
if __name__ == "__main__":
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    generate_pdf(data)