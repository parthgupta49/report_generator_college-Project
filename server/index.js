// server.js
const express = require('express');
const multer = require('multer');
const { exec } = require('node:child_process');
const path = require('node:path');
const fs = require('node:fs');
const cors = require('cors')
const app = express();
const upload = multer({ dest: 'uploads/' });
app.use(cors({
    origin : "http://localhost:3000",
    // origin : "https://task-manager-assignment-application.vercel.app",
    credentials : true
}));

app.post('/generate-pdf', upload.any(), (req, res) => {
    // Extract JSON data
    const jsonData = JSON.parse(req.body.data);

    // Organize files
    const files = {
        signatures: {
            // organizer: req.files.find(f => f.fieldname.startsWith('organizer_signature'))?.path,
            hod: req.files.find(f => f.fieldname.startsWith('hod_signature'))?.path
        },
        annexure: {}
    };

    // Process annexure files
    req.files.forEach(file => {
        const field = file.fieldname;

        if (field.startsWith('speaker_profile')) {
            files.annexure.speaker_profile = files.annexure.speaker_profile || [];
            files.annexure.speaker_profile.push(file.path);
        }
        else if (field.startsWith('activity_photos')) {
            files.annexure.activity_photos = files.annexure.activity_photos || [];
            files.annexure.activity_photos.push(file.path);
        }
        else if (field.startsWith('attendance')) {
            files.annexure.attendance = files.annexure.attendance || [];
            files.annexure.attendance.push(file.path);
        }
        else if (field.startsWith('brochure/poster')) {
            files.annexure.brochure_poster = files.annexure.brochure_poster || [];
            files.annexure.brochure_poster.push(file.path);
        }
        else if (field.startsWith('website_screenshots')) {
            files.annexure.website_screenshots = files.annexure.website_screenshots || [];
            files.annexure.website_screenshots.push(file.path);
        }
        else if (field.startsWith('student_feedback')) {
            files.annexure.student_feedback = files.annexure.student_feedback || [];
            files.annexure.student_feedback.push(file.path);
        }
        else if (field.startsWith('action_taken_report')) {
            files.annexure.action_taken_report = files.annexure.action_taken_report || [];
            files.annexure.action_taken_report.push(file.path);
        }
    });

    // Prepare final payload
    const payload = {
        ...jsonData,
        files
    };

    // Save to temporary file
    const tempFile = path.join(__dirname, 'temp_payload.json');
    fs.writeFileSync(tempFile, JSON.stringify(payload));

    // Execute Python script
    exec(`python main3.py ${tempFile}`, async (error) => {
        try {
            if (error) throw error;

            // Verify PDF exists
            if (!fs.existsSync('output.pdf')) {
                throw new Error('Python script did not generate output.pdf');
            }

            // Send PDF
            const pdf = fs.readFileSync('output.pdf');
            res.setHeader('Content-Type', 'application/pdf');
            res.setHeader('Content-Disposition', 'attachment; filename=report.pdf');
            res.send(pdf);

        } catch (err) {
            console.error('Error:', err);
            res.status(500).json({
                message: '-------- Internal Server Error ------',
                error: err.message,
                success : false
            })
        } finally {
            // Cleanup all temporary files
            const filesToDelete = [
                tempFile,
                'output.pdf',
                ...req.files.map(f => f.path)
            ];

            for (const file of filesToDelete) {
                try {
                    if (fs.existsSync(file)) {
                        fs.unlinkSync(file);
                        console.log(`Cleaned up: ${file}`);
                    }
                } catch (err) {
                    console.error(`Failed to delete ${file}:`, err);
                }
            }
        }
    });
});

app.listen(3001, () => console.log('Server running on port 3001'));