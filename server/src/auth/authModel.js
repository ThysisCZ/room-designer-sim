//dependencies
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

//schema library
const Schema = mongoose.Schema;

//initialize user schema
const userSchema = new Schema({
    username: {
        type: String,
        required: true,
        unique: true
    },
    email: {
        type: String,
        required: true,
        unique: true
    },
    password: {
        type: String,
        required: true
    },
    reset_code: {
        type: String,
        default: null
    },
    reset_code_expires: {
        type: Date,
        default: null
    },
    created_at: {
        type: Date,
        default: Date.now
    },
    last_login: {
        type: Date,
        default: Date.now
    }
});

//hash password with 16 cost factor rounds
userSchema.pre('save', async function (next) {
    if (!this.isModified('password')) return next();
    this.password = await bcrypt.hash(this.password, 16);
    next();
});

//compare password method
userSchema.methods.comparePassword = async function (password) {
    return await bcrypt.compare(password, this.password);
};

//generate password reset code
userSchema.methods.generateResetCode = function () {
    //generate 6-digit code
    const code = Math.floor(100000 + Math.random() * 900000).toString();
    this.reset_code = code;
    //code expires in 15 minutes
    this.reset_code_expires = Date.now() + 15 * 60 * 1000;
    return code;
};

//verify reset code
userSchema.methods.verifyResetCode = function (code) {
    return this.reset_code === code && this.reset_code_expires > Date.now();
};

//clear reset code after use
userSchema.methods.clearResetCode = function () {
    this.reset_code = null;
    this.reset_code_expires = null;
};

//export user model
module.exports = mongoose.model('User', userSchema, 'users');