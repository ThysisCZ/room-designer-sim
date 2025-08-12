const authService = require('./authService');

async function registerController(req, res) {
    try {
        const result = await authService.registerUserService(req.body);
        res.status(201).send({ "status": true, "message": "User registered successfully.", "data": result });
    } catch (error) {
        res.status(400).send({ "status": false, "message": error.message });
    }
}

async function loginController(req, res) {
    try {
        const result = await authService.loginUserService(req.body);
        res.status(200).send({ "status": true, "message": "Login successful.", "data": result });
    } catch (error) {
        res.status(401).send({ "status": false, "message": error.message });
    }
}

async function forgotPasswordController(req, res) {
    try {
        const result = await authService.forgotPasswordService(req.body.email);
        res.status(200).send({ "status": true, "message": "Reset code sent to your email.", "data": result });
    } catch (error) {
        res.status(400).send({ "status": false, "message": error.message });
    }
}

async function resetPasswordController(req, res) {
    try {
        const result = await authService.resetPasswordService(req.body);
        res.status(200).send({ "status": true, "message": "Password reset successfully.", "data": result });
    } catch (error) {
        res.status(400).send({ "status": false, "message": error.message });
    }
}

module.exports = {
    registerController,
    loginController,
    forgotPasswordController,
    resetPasswordController
}