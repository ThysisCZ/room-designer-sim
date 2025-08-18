//dependencies
const mongoose = require('mongoose');

//schema library
const Schema = mongoose.Schema;

//initialize game data schema
const gameDataSchema = new Schema({
    user_id: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true,
        unique: true
    },
    inventory: {
        item: {
            type: [{
                id: { type: String, required: true },
                name: { type: String, required: true },
                spritesheet: { type: String, required: true },
                type: { type: String, required: true },
                description: { type: String, required: true },
                price: { type: Number, required: true },
                count: { type: Number, required: true }
            }],
            default: []
        },
        floor: {
            type: [{
                id: { type: String, required: true },
                name: { type: String, required: true },
                spritesheet: { type: String, required: true },
                type: { type: String, required: true },
                description: { type: String, required: true },
                price: { type: Number, required: true }
            }],
            default: []
        },
        wall: {
            type: [{
                id: { type: String, required: true },
                name: { type: String, required: true },
                spritesheet: { type: String, required: true },
                type: { type: String, required: true },
                description: { type: String, required: true },
                price: { type: Number, required: true }
            }],
            default: []
        }
    },
    selection: {
        floor: {
            id: { type: String, default: '' },
            name: { type: String, default: '' },
            spritesheet: { type: String, default: '' },
            type: { type: String, default: '' },
            description: { type: String, default: '' },
            price: { type: Number, default: 0 }
        },
        wall: {
            id: { type: String, default: '' },
            name: { type: String, default: '' },
            spritesheet: { type: String, default: '' },
            type: { type: String, default: '' },
            description: { type: String, default: '' },
            price: { type: Number, default: 0 }
        }
    },
    stats: {
        total_balance: { type: Number, default: 0 },
        snake_hi_score: { type: Number, default: 0 },
        fruit_hi_score: { type: Number, default: 0 },
        bullet_hi_score: { type: Number, default: 0 }
    },
    tiles: [{
        "grid_x": Number,
        "grid_y": Number,
        "grid_z": Number,
        "col": Number,
        "row": Number,
        "id": String
    }],
    updated_at: {
        type: Date,
        default: Date.now
    }
});

//update timestamp before saving
gameDataSchema.pre('save', function (next) {
    this.updated_at = new Date();
    next();
});

//export game data model
module.exports = mongoose.model('GameData', gameDataSchema, 'gamedata');