//dependencies
const userModel = require('./authModel');

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