// const nodemailer = require('nodemailer');
// require('dotenv').config();
// exports.mailSender = async (email,body) => {
//     try {
//         console.log("hello ji in nodemailer.js")
//         console.log("email : ",email)
//         const transporter = nodemailer.createTransport({
//             host: process.env.MAIL_HOST,
//             auth: {
//                 user: process.env.MAIL_USER,
//                 pass: process.env.MAIL_PASS,
//             },
//         });
    
//         // async..await is not allowed in global scope, must use a wrapper
//         // send mail with defined transport object
//         const info = await transporter.sendMail({
//             from: 'nbparthgupta4959@gmail.com', // sender address
//             to: email, // list of receivers
//             subject: `Newsletter`, // Subject line
//             // text: `OTP lelo ${body}`, // plain text body
//             html: `${body}`, // html body
//         });
    
//         console.log("Message sent: %s", info.messageId);
//         return info;
//     } catch (error) {
//         console.error(error);
//         console.log("Couldn't send the email")
//     }
// }


const nodemailer = require('nodemailer');
// require('dotenv').config();
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