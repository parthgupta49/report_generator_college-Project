const express = require('express');
const multer = require('multer');
const { exec } = require('node:child_process');
const path = require('node:path');
const fs = require('node:fs');
const cors = require('cors')
const app = express();
const upload = multer({ dest: 'uploads/' });
const {mailSender} = require('./utils/nodemailer')

const PDFServicesSdk = require('@adobe/pdfservices-node-sdk');
const { ServicePrincipalCredentials, PDFServices, MimeType, ExportPDFJob, ExportPDFParams, ExportPDFTargetFormat, ExportPDFResult } = PDFServicesSdk;

const allowedOrigins = [
    "https://csbyc-event-report-generator.vercel.app",
    "http://localhost:3000"
]

app.use(cors({
    origin : allowedOrigins,
    credentials: true
}));

app.options('*',cors());

// Function to convert PDF to DOCX
async function convertPdfToDocx(pdfFilePath, docxFilePath) {
    try {
        // Create a read stream for the input PDF file
        const readStream = fs.createReadStream(pdfFilePath);
        const clientId = process.env.ADOBE_CLIENT_ID
        const clientSecret = process.env.ADOBE_CLIENT_SECRET


        // Set up credentials
        const credentials = new ServicePrincipalCredentials({
            clientId: clientId, // Replace with your Client ID
            clientSecret: clientSecret // Replace with your Client Secret
        });

        // Create an instance of PDFServices
        const pdfServices = new PDFServices({ credentials });

        // Upload the PDF file as an asset
        const inputAsset = await pdfServices.upload({
            readStream,
            mimeType: MimeType.PDF
        });

        // Set up parameters for the export job
        const params = new ExportPDFParams({
            targetFormat: ExportPDFTargetFormat.DOCX
        });

        // Create the export job
        const job = new ExportPDFJob({ inputAsset, params });

        // Submit the job
        const pollingURL = await pdfServices.submit({ job });

        // Get the job result
        const pdfServicesResponse = await pdfServices.getJobResult({
            pollingURL,
            resultType: ExportPDFResult
        });

        // Get the result asset
        const resultAsset = pdfServicesResponse.result.asset;

        // Get the content of the result asset
        const streamAsset = await pdfServices.getContent({ asset: resultAsset });

        // Check if _readStream is defined
        if (streamAsset && streamAsset._readStream) {
            // Save the output DOCX file
            const writeStream = fs.createWriteStream(docxFilePath);
            streamAsset._readStream.pipe(writeStream);

            return new Promise((resolve, reject) => {
                writeStream.on('finish', () => {
                    console.log('PDF successfully converted to DOCX and saved as', docxFilePath);
                    resolve();
                });
                writeStream.on('error', (err) => {
                    console.error('Error writing DOCX file:', err);
                    reject(err);
                });
            });
        } else {
            throw new Error('Error: streamAsset is undefined or does not have a _readStream property.');
        }
    } catch (err) {
        console.error('Error converting PDF to DOCX:', err);
        throw err; // Rethrow the error to be handled in the calling function
    }
}

app.post('/generate-pdf', upload.any(), (req, res) => {

    res.header('Access-Control-Allow-Origin', 'https://csbyc-event-report-generator.vercel.app');
    res.header('Access-Control-Allow-Credentials', 'true');


    // Extract JSON data and action type
    const jsonData = JSON.parse(req.body.data);
    const action = req.body.action || 'report'; // Default to report

    const newsletterFormat = req.body.newsletterFormat || 'pdf';

    // Extract newsletter email from form data
    const newsletterEmail = req.body.newsletterEmail;
    if (newsletterEmail) {
        console.log(newsletterEmail);
    }

    // Organize files
    const files = {
        signatures: {
            organizer: req.files.find(f => f.fieldname.startsWith('organizer_signature'))?.path,
            hod: req.files.find(f => f.fieldname.startsWith('hod_signature'))?.path
        },
        annexure: {},
        speaker_profile: {
            speakerProfile: req.files.find(f => f.fieldname.startsWith('speaker_profile'))?.path
        }
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

    // Prepare final payload with action type
    const payload = {
        ...jsonData,
        files,
        action: action
    };

    // Save to temporary file
    const tempFile = path.join(__dirname, 'temp_payload.json');
    fs.writeFileSync(tempFile, JSON.stringify(payload));

    // Execute Python script
    exec(`python main3.py ${tempFile}`, async (error) => {
        try {
            if (error) throw error;

            // Determine output filename based on action
            const outputFilename = action === 'newsletter' ? 'newsletter.pdf' : 'output.pdf';

            // Verify PDF exists
            if (!fs.existsSync(outputFilename)) {
                throw new Error(`Python script did not generate ${outputFilename}`);
            }

            // If the format is DOCX, convert the PDF to DOCX
            if (newsletterFormat === 'docx' && action === 'newsletter') {
                const docxFilename = 'newsletter.docx'; // Desired output file path for DOCX
                await convertPdfToDocx(outputFilename, docxFilename);
                
            // Verify DOCX exists
            if (!fs.existsSync(docxFilename)) {
                throw new Error(`Conversion did not generate ${docxFilename}`);
            }
            // Send the DOCX file to the user
            const docxBuffer = fs.readFileSync(docxFilename);

            // Send the DOCX file to the user
            res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');
            res.setHeader('Content-Disposition', `attachment; filename="${docxFilename}"`);
            // Then handle email sending if needed (non-blocking)
            if (docxFilename === "newsletter.docx" && newsletterEmail  ) {
                try {
                    const pdfBuffer = fs.readFileSync(docxFilename);
                    await mailSender(
                        newsletterEmail,
                        `<p>Please find attached the newsletter.</p>`,
                        {
                            filename: 'newsletter.docx',
                            content: pdfBuffer
                        }
                    );
                    console.log('Email sent successfully');
                } catch (emailError) {
                    console.error('Email sending failed:', emailError);
                    // Consider logging this to an error tracking service
                }
            }
            return res.send(docxBuffer);
            }

            // Send PDF
            const pdf = fs.readFileSync(outputFilename);
            res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, private');
            res.setHeader('Pragma', 'no-cache');
            res.setHeader('Expires', '0');
            res.setHeader('Content-Type', 'application/pdf');
            res.setHeader('Content-Disposition', `attachment; filename="${outputFilename}"`);
            res.send(pdf);

            // Then handle email sending if needed (non-blocking)
            if (outputFilename === "newsletter.pdf" && newsletterEmail  ) {
                try {
                    const pdfBuffer = fs.readFileSync(outputFilename);
                    await mailSender(
                        newsletterEmail,
                        `<p>Please find attached the newsletter.</p>`,
                        {
                            filename: 'newsletter.pdf',
                            content: pdfBuffer
                        }
                    );
                    console.log('Email sent successfully');
                } catch (emailError) {
                    console.error('Email sending failed:', emailError);
                    // Consider logging this to an error tracking service
                }
            }

        } catch (err) {
            console.error('Error:', err);
            res.status(500).json({
                message: 'Internal Server Error',
                error: err.message,
                success: false
            });
        } finally {
            // Cleanup all temporary files
            const filesToDelete = [
                tempFile,
                ...(action === 'report' ? ['output.pdf'] : []),
                ...(action === 'newsletter' ? ['newsletter.pdf'] : []),
                ...(action === 'newsletter' && newsletterFormat==='docx' ? ['newsletter.docx'] : []),
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