const nodemailer = require('nodemailer');
exports.mailSender = async (email, body, attachment = null) => {
    try {
        const transporter = nodemailer.createTransport({
            host: process.env.MAIL_HOST,
            auth: {
                user: process.env.MAIL_USER,
                pass: process.env.MAIL_PASS,
            },
        });

        const mailOptions = {
            from: process.env.MAIL_USER,
            to: email,
            subject: 'Event Newsletter',
            html: body,
            attachments: []
        };

        if (attachment) {
            mailOptions.attachments.push({
                filename: attachment.filename,
                content: attachment.content
            });
        }

        const info = await transporter.sendMail(mailOptions);
        console.log("Message sent: %s", info.messageId);
        return info;
    } catch (error) {
        console.error("Email send error:", error);
        throw error;
    }
}