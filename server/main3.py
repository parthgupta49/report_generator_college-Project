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

# def generate_pdf(data, output_filename="output.pdf"):
#     c = canvas.Canvas(output_filename, pagesize=letter)
#     page_width, page_height = letter
#     margin_top = 72  # 1 inch from top
#     margin_bottom = 36  # 0.5 inches from bottom
#     current_page = 1

#     # --- Custom Header ---
#     def draw_header():
#         # Logo on the right
#         try:
#             logo = ImageReader("logo.png")
#             logo_width, logo_height = 200, 75
#             c.drawImage(logo, page_width - 50 - logo_width, page_height - margin_top - 20,width=logo_width, height=logo_height)
            
#             # Department text below logo
#             dept_text = "Dept. of Computer Science - Bangalore Yeshwanthpur Campus"
#             c.setFont("Helvetica", 8)
#             c.drawRightString(page_width - 70, page_height - margin_top - 20, dept_text)
#         except:
#             pass

#         # Left side content
#         c.setFont("Helvetica-Bold", 12)
#         c.drawString(120, page_height - margin_top - 20, "Event / Activity Report")

#         # Activity and Date inputs
#         c.setFont("Helvetica", 12)
#         y_position = page_height - margin_top - 60
#         c.drawString(50, y_position, f"Activity: {data['header']['activityName']}")
#         c.drawString(50, y_position - 20, f"Date(s): {data['header']['activityDate']}")

#         # Horizontal line
#         c.setStrokeColor(HexColor("#4472c4"))
#         c.line(50, y_position - 28, page_width - 50, y_position - 28)

#     # --- Footer ---
#     def draw_footer():
#         c.setFont("Helvetica", 12)
#         c.setFillColor(HexColor("#0"))
#         c.drawString(50, margin_bottom + 10, "   # CS_BYC")
#         c.drawRightString(page_width - 110, margin_bottom + 10, f"{current_page}")
#         c.setStrokeColor(HexColor("#4472c4"))
#         c.line(50, margin_bottom + 25, page_width - 50, margin_bottom + 25)

#     # --- Table Creation ---
#     def create_table(heading, data, y_start):
#         styles = getSampleStyleSheet()
#         styles["Normal"].fontName = "Helvetica"
#         styles["Normal"].fontSize = 10
#         styles["Normal"].leading = 12
        
#         # Create a new style for the heading with white text
#         heading_style = styles["Normal"]
#         heading_style.textColor = HexColor("#000000")  # Set text color to white

#         # table_data = [[Paragraph(f"<b>{heading}</b>", styles["Normal"]), ""]]
        
#         # Use the new style for the heading
#         table_data = [[Paragraph(f"<b>{heading}</b>", heading_style), ""]]
#         for label, value in data:
#             wrapped_label = Paragraph(f"<b>{label}</b>", styles["Normal"])
            
#             # # Handle signature image
#             # if label == "Signature:" and value:
#             #     try:
#             #         img = Image.open(value)
#             #         img_w, img_h = img.size
#             #         aspect = img_w / img_h
#             #         max_w = 150
#             #         scaled_w = min(max_w, img_w)
#             #         scaled_h = scaled_w / aspect
#             #         wrapped_value = PlatypusImage(value, width=scaled_w, height=scaled_h)
#             #     except:
#             #         wrapped_value = Paragraph("[Signature]", styles["Normal"])
#             # else:
#             #     wrapped_value = Paragraph(str(value), styles["Normal"])
#             wrapped_value = Paragraph(str(value), styles["Normal"])
#             table_data.append([wrapped_label, wrapped_value])

#         # Table styling
#         style = TableStyle([
#             ('SPAN', (0,0), (1,0)),
#             ('BACKGROUND', (0,0), (-1,0), HexColor("#7399c9")),
#             ('TEXTCOLOR', (0,0), (-1,0), HexColor("#FFFFFF")),
#             ('BACKGROUND', (0,1), (0,-1), lightgrey),
#             ('GRID', (0,0), (-1,-1), 0.5, HexColor("#171616")),
#             ('VALIGN', (0,0), (-1,-1), 'TOP'),
#         ])

#         table = Table(table_data, colWidths=[150, 350])
#         table.setStyle(style)
#         table.wrapOn(c, page_width, page_height)
#         table_height = table._height

#         # Page break check
#         if (y_start - table_height) < margin_bottom + 100:
#             c.showPage()
#             nonlocal current_page
#             current_page += 1
#             draw_header()
#             draw_footer()
#             y_start = page_height - margin_top - 100

#         # Draw table
#         table.drawOn(c, 50, y_start - table_height)
#         return y_start - table_height - 20

#     # --- HOD Section ---
#     def add_hod_section(y_position, current_page):
#         hod_signature = data.get('files', {}).get('signatures', {}).get('hod', '')
        
#         # Calculate space needed (conservative estimate including image)
#         max_image_height = 100  # Assuming max height for space check
#         required_space = 30 + 10 + max_image_height + 20 + 40  # line + spacing + image + text spacing + text

#         # Check page space
#         if (y_position - required_space) < margin_bottom:
#             c.showPage()
#             current_page += 1
#             draw_header()
#             draw_footer()
#             y_position = page_height - margin_top - 100
        
        
#         if not hod_signature:
#             return y_position, current_page

#         try:
#             img = Image.open(hod_signature)
#             img_w, img_h = img.size
#             aspect = img_w / img_h
#             max_w = 100
#             scaled_w = min(max_w, img_w)
#             scaled_h = scaled_w / aspect

#             # Position calculations
#             right_margin = page_width - 50
#             image_x = right_margin - scaled_w
#             image_y = y_position - scaled_h - 20

#             # Draw image
#             c.drawImage(hod_signature, image_x, image_y, width=scaled_w, height=scaled_h)

#             # Draw text
#             text_y = image_y - 20
#             c.setFont("Helvetica-Bold", 12)
#             c.drawRightString(right_margin, text_y, "Head of the Department")
#             c.setFont("Helvetica", 12)
#             c.drawRightString(right_margin, text_y - 20, "(Vinay M)")

#             return text_y - 40, current_page
#         except:
#             return y_position, current_page

#     # --- Annexure Handling ---
#     def add_annexure(y_position, current_page):
#         annex_data = data.get('files', {}).get('annexure', {})
#         sections = [
#             ('speaker_profile', "1. Speaker Profile"),
#             ('activity_photos', "2. Photos of the activity"),
#             ('attendance', "3. Attendance of participants"),
#             ('brochure_poster', "4. Brochure/Poster"),
#             ('website_screenshots', "5. Website Screenshots"),
#             ('student_feedback', "6. Student Feedback"),
#             ('action_taken_report', "7. Action Taken Report")
#         ]
#         # y_position-=20

#         for field, heading in sections:
#             images = annex_data.get(field, [])
#             if not images:
#                 continue

#             # Check page space
#             if y_position < margin_bottom + 200:
#                 c.showPage()
#                 current_page += 1
#                 draw_header()
#                 draw_footer()
#                 y_position = page_height - margin_top - 100 - 18

#             # Add heading
#             c.setFont("Helvetica-Bold", 12)
#             c.drawString(50, y_position, heading)
#             y_position -= 20

#             # Draw images in grid
#             x_pos = 50
#             max_width = 150
#             row_height = 0
            
#             for img_path in images:
#                 try:
#                     img = Image.open(img_path)
#                     img_w, img_h = img.size
#                     aspect = img_w / img_h
#                     scaled_w = min(max_width, img_w)
#                     scaled_h = scaled_w / aspect

#                     if x_pos + scaled_w > page_width - 50:
#                         x_pos = 50
#                         y_position -= row_height + 15
#                         row_height = 0

#                     if y_position - scaled_h < margin_bottom:
#                         c.showPage()
#                         current_page += 1
#                         draw_header()
#                         draw_footer()
#                         y_position = page_height - margin_top - 100
#                         x_pos = 50
#                         row_height = 0

#                     c.drawImage(img_path, x_pos, y_position - scaled_h, width=scaled_w, height=scaled_h)
#                     x_pos += scaled_w + 15
#                     row_height = max(row_height, scaled_h)
#                 except:
#                     continue

#             y_position -= row_height + 30

#         return y_position, current_page

#     # --- Main Content Flow ---
#     def add_content():
#         nonlocal current_page
#         y_pos = page_height - margin_top - 105
        
#         # Activity Report Title
#         c.setFont("Helvetica-Bold", 10)
#         c.drawCentredString(page_width/2, y_pos, "Activity Report")
#         y_pos -= 10

#         # Main Tables
#         tables = [
#             ("General Information", [
#                 ("Type of Activity:", data["generalInfo"]["type"]),
#                 ("Title of Activity:", data["generalInfo"]["title"]),
#                 ("Time:", data["generalInfo"]["time"]),
#                 ("Venue:", data["generalInfo"]["venue"]),
#                 ("Collaboration/Sponsor:", data["generalInfo"]["collaboration"]),
#                 ("SDGs Linked:", data["generalInfo"]["sdgs"]),
#                 ("Website/Platform:", data["generalInfo"]["website"]),
#                 ("Video Links:", data["generalInfo"]["videos"])
#             ]),
#             ("Speaker Details", [
#                 ("Name:", data["speaker"]["name"]),
#                 ("Title/Position:", data["speaker"]["title"]),
#                 ("Organization:", data["speaker"]["organization"]),
#                 ("Presentation Title:", data["speaker"]["presentation"])
#             ]),
#             ("Participants Profile", [
#                 ("Type of Participants:", data["participants"]["type"]),
#                 ("Total Participants:", data["participants"]["total"]),
#                 ("CHRIST Students:", data["participants"]["christStudents"]),
#                 ("CHRIST Faculty:", data["participants"]["christFaculty"]),
#                 ("Other Students:", data["participants"]["otherStudents"]),
#                 ("Other Faculty/Participants:", data["participants"]["otherFaculty"])
#             ]),
#             ("Synopsis", [
#                 ("Highlights:", data["synopsis"]["highlights"]),
#                 ("Key Takeaways:", data["synopsis"]["takeaways"]),
#                 ("Summary:", data["synopsis"]["summary"]),
#                 ("Follow-up Plan:", data["synopsis"]["followup"])
#             ]),
#             ("Report Prepared By", [
#                 ("Name of Organiser:", data["reportPrepared"]["name"]),
#                 ("Designation/Title:", data["reportPrepared"]["designation"]),
#                 ("Signature:", data["reportPrepared"]["Signature"])
#             ])
#         ]

#         for heading, rows in tables:
#             y_pos = create_table(heading, rows, y_pos)
#             if y_pos < margin_bottom + 100:
#                 c.showPage()
#                 current_page += 1
#                 draw_header()
#                 draw_footer()
#                 y_pos = page_height - margin_top - 100

#         # Add HOD section
#         y_pos, current_page = add_hod_section(y_pos, current_page)

#         # Add annexure
#         y_pos, current_page = add_annexure(y_pos, current_page)
        
#         # Add HOD section
#         y_pos, current_page = add_hod_section(y_pos, current_page)

#     # --- Execution ---
#     draw_header()
#     draw_footer()
#     add_content()
#     c.save()

# if __name__ == "__main__":
#     with open(sys.argv[1], 'r') as f:
#         data = json.load(f)
#     generate_pdf(data)


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
        if (y_start - table_height) < margin_bottom + 100:
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
        
        if not hod_signature:
            return y_position

        try:
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

    # --- Annexure Handling ---
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
        sections = [
            ('speaker_profile', "1. Speaker Profile"),
            ('activity_photos', "2. Photos of the activity"),
            ('attendance', "3. Attendance of participants"),
            ('brochure_poster', "4. Brochure/Poster"),
            ('website_screenshots', "5. Website Screenshots"),
            ('student_feedback', "6. Student Feedback"),
            ('action_taken_report', "7. Action Taken Report")
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
            x_pos = 50
            max_width = 150
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
            ]),
            ("Report Prepared By", [
                ("Name of Organiser:", data["reportPrepared"]["name"]),
                ("Designation/Title:", data["reportPrepared"]["designation"]),
                ("Signature:", data["reportPrepared"]["Signature"])
            ])
        ]

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