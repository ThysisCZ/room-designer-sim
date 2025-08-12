//dependencies
const userModel = require('./authModel');
const nodemailer = require('nodemailer');

// Email configuration
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS
    },
    tls: {
        rejectUnauthorized: false
    }
});

// Test email configuration on startup
transporter.verify((error, success) => {
    if (error) {
        console.error('Email configuration error:', error);
    } else {
        console.log('Email server is ready to send messages');
    }
});

module.exports.registerUserService = (userDetails) => {
    return new Promise((resolve, reject) => {
        const userModelData = new userModel();

        userModelData.username = userDetails.username;
        userModelData.email = userDetails.email;
        userModelData.password = userDetails.password;

        userModelData.save()
            .then((result) => {
                resolve({ success: true, userId: result._id });
            })
            .catch((error) => {
                if (error.code === 11000) {
                    reject({ success: false, message: "Username or email already exists" });
                } else {
                    reject({ success: false, message: "Registration failed" });
                }
            });
    });
}

module.exports.loginUserService = (loginDetails) => {
    return new Promise((resolve, reject) => {
        // Check if login credential is email or username
        const isEmail = loginDetails.username.includes('@');
        const query = isEmail
            ? { email: loginDetails.username }
            : { username: loginDetails.username };

        userModel.findOne(query)
            .then(async (user) => {
                if (!user) {
                    reject({ success: false, message: "Username or email doesn't exist" });
                    return;
                }

                const isValidPassword = await user.comparePassword(loginDetails.password);
                if (!isValidPassword) {
                    reject({ success: false, message: "Invalid password" });
                    return;
                }

                //update last login
                user.last_login = new Date();
                await user.save();

                resolve({ success: true, userId: user._id, username: user.username });
            })
            .catch(() => {
                reject({ success: false, message: "Login failed" });
            });
    });
}

module.exports.forgotPasswordService = (email) => {
    return new Promise((resolve, reject) => {
        // First check if email configuration is available
        if (!process.env.EMAIL_USER || !process.env.EMAIL_PASS) {
            console.error('Email configuration missing: EMAIL_USER or EMAIL_PASS not set');
            reject({ success: false, message: "Email service temporarily unavailable" });
            return;
        }

        userModel.findOne({ email: email })
            .then(async (user) => {
                if (!user) {
                    reject({ success: false, message: "No account found with this email address" });
                    return;
                }

                // Generate reset code
                const resetCode = user.generateResetCode();
                await user.save();

                // Send email with reset code
                const mailOptions = {
                    from: `"Room Designer Simulator" <${process.env.EMAIL_USER}>`,
                    to: email,
                    subject: 'Room Designer Simulator - Password Reset Code',
                    html: `
                        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                            <h2 style="color: #333;">Password Reset Request</h2>
                            <p>You requested a password reset for your Room Designer Simulator account.</p>
                            <p>Your reset code is:</p>
                            <div style="background-color: #f0f0f0; padding: 20px; text-align: center; margin: 20px 0;">
                                <h1 style="color: #333; font-size: 36px; letter-spacing: 5px; margin: 0;">${resetCode}</h1>
                            </div>
                            <p>This code will expire in 15 minutes.</p>
                            <p>If you didn't request this reset, you can safely ignore this email.</p>
                            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                            <p style="color: #666; font-size: 12px;">Room Designer Simulator - Keep Building!</p>
                        </div>
                    `
                };

                console.log('Attempting to send email to:', email);

                transporter.sendMail(mailOptions)
                    .then((info) => {
                        console.log('Email sent successfully:', info.messageId);
                        resolve({ success: true, message: "Reset code sent to your email" });
                    })
                    .catch((error) => {
                        console.error('Email sending failed:', error);

                        // More specific error messages
                        let errorMessage = "Failed to send reset email";
                        if (error.code === 'EAUTH') {
                            errorMessage = "Email authentication failed - check email credentials";
                        } else if (error.code === 'ECONNECTION') {
                            errorMessage = "Could not connect to email server";
                        } else if (error.response && error.response.includes('535')) {
                            errorMessage = "Invalid email credentials - please check app password";
                        }

                        reject({ success: false, message: errorMessage });
                    });
            })
            .catch((dbError) => {
                console.error('Database error in forgot password:', dbError);
                reject({ success: false, message: "Password reset request failed" });
            });
    });
}

module.exports.resetPasswordService = (resetDetails) => {
    return new Promise((resolve, reject) => {
        userModel.findOne({ email: resetDetails.email })
            .then(async (user) => {
                if (!user) {
                    reject({ success: false, message: "No account found with this email address" });
                    return;
                }

                // Verify reset code
                if (!user.verifyResetCode(resetDetails.resetCode)) {
                    reject({ success: false, message: "Invalid or expired reset code" });
                    return;
                }

                // Update password
                user.password = resetDetails.newPassword;
                user.clearResetCode();
                await user.save();

                resolve({ success: true, message: "Password reset successfully" });
            })
            .catch((dbError) => {
                console.error('Database error in reset password:', dbError);
                reject({ success: false, message: "Password reset failed" });
            });
    });
}