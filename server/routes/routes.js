//dependencies
const express = require('express');
const authController = require('../src/auth/authController');
const gameDataController = require('../src/gameData/gameDataController');

//initialize router
const router = express.Router();

//authentication routes
router.route('/auth/register').post(authController.registerController);
router.route('/auth/login').post(authController.loginController);

//game data routes
router.route('/gamedata/save/:userId').post(gameDataController.saveGameDataController);
router.route('/gamedata/load/:userId').get(gameDataController.loadGameDataController);
router.route('/gamedata/sync/:userId').patch(gameDataController.syncGameDataController);

//export router
module.exports = router;