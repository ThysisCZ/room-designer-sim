const gameDataService = require('./gameDataService');

async function saveGameDataController(req, res) {
    try {
        const userId = req.params.userId;
        const gameData = req.body;

        console.log('Saving data for user:', userId);
        console.log('Game data received:', JSON.stringify(gameData, null, 2));

        const result = await gameDataService.saveGameDataService(userId, gameData);

        if (result) {
            res.send({ "status": true, "message": "Game data saved successfully.", "data": result });
        } else {
            res.status(500).send({ "status": false, "message": "Error saving game data." });
        }
    } catch (e) {
        console.error('Save game data error:', e);
        res.status(500).send({ message: 'Server error.', error: e.message });
    }
}

async function loadGameDataController(req, res) {
    try {
        const userId = req.params.userId;
        const gameData = await gameDataService.loadGameDataService(userId);

        if (gameData) {
            res.status(200).send({ "status": true, "data": gameData });
        } else {
            res.status(404).send({ message: 'Game data not found.' });
        }
    } catch (e) {
        console.error(e);
        res.status(500).send({ message: 'Server error.' });
    }
}

async function syncGameDataController(req, res) {
    try {
        const userId = req.params.userId;
        const gameData = req.body.gameData;
        const lastSyncTime = req.body.lastSyncTime;

        const result = await gameDataService.syncGameDataService(userId, gameData, lastSyncTime);

        if (result) {
            res.send({
                "status": true,
                "message": `Game data ${result.action}ed successfully.`,
                "action": result.action,
                "data": result.data
            });
        } else {
            res.status(500).send({ "status": false, "message": "Error syncing game data." });
        }
    } catch (e) {
        console.error(e);
        res.status(500).send({ message: 'Server error.' });
    }
}

module.exports = {
    saveGameDataController,
    loadGameDataController,
    syncGameDataController
}