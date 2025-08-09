//dependencies
const gameDataModel = require('./gameDataModel');

module.exports.saveGameDataService = (userId, gameData) => {
    return new Promise((resolve, reject) => {
        const updateData = {
            user_id: userId,
            inventory: gameData.inventory || { item: [], floor: [], wall: [] },
            selection: gameData.selection || {
                floor: { id: '', name: '', spritesheet: '', type: '', description: '', price: 0 },
                wall: { id: '', name: '', spritesheet: '', type: '', description: '', price: 0 }
            },
            stats: gameData.stats || { total_balance: 0, snake_hi_score: 0, fruit_hi_score: 0, bullet_hi_score: 0 },
            tiles: gameData.tiles || [],
            updated_at: new Date()
        };

        console.log('Attempting to save with updateData:', JSON.stringify(updateData, null, 2));

        gameDataModel.findOneAndUpdate(
            { user_id: userId },
            { $set: updateData },
            { new: true, upsert: true }
        )
            .then((result) => {
                console.log('Save successful:', result);
                resolve(result);
            })
            .catch((error) => {
                console.error('Save failed with error:', error);
                reject(error);
            });
    });
}

module.exports.loadGameDataService = (userId) => {
    return new Promise((resolve, reject) => {
        gameDataModel.findOne({ user_id: userId })
            .then((result) => {
                if (result) {
                    resolve(result);
                } else {
                    //return default structure if no data found
                    const defaultData = {
                        user_id: userId,
                        inventory: { item: [], floor: [], wall: [] },
                        selection: {
                            floor: { id: '', name: '', spritesheet: '', type: '', description: '', price: 0 },
                            wall: { id: '', name: '', spritesheet: '', type: '', description: '', price: 0 }
                        },
                        stats: { total_balance: 0, snake_hi_score: 0, fruit_hi_score: 0, bullet_hi_score: 0 },
                        tiles: [],
                        updated_at: new Date()
                    };
                    resolve(defaultData);
                }
            })
            .catch(() => {
                reject(false);
            });
    });
}

module.exports.syncGameDataService = (userId, gameData, lastSyncTime) => {
    return new Promise((resolve, reject) => {
        gameDataModel.findOne({ user_id: userId })
            .then((existingData) => {
                if (!existingData || new Date(existingData.updated_at) <= new Date(lastSyncTime)) {
                    //local data is newer or no cloud data exists, update cloud
                    return module.exports.saveGameDataService(userId, gameData);
                } else {
                    //cloud data is newer, return it
                    resolve({ action: 'download', data: existingData });
                }
            })
            .then((result) => {
                if (result && result.action !== 'download') {
                    resolve({ action: 'upload', data: result });
                }
            })
            .catch((error) => {
                console.error('Sync error:', error);
                reject(false);
            });
    });
}