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

        // Avoid logging large payloads; log only counts
        const invCounts = {
            item: Array.isArray(updateData.inventory?.item) ? updateData.inventory.item.length : 0,
            floor: Array.isArray(updateData.inventory?.floor) ? updateData.inventory.floor.length : 0,
            wall: Array.isArray(updateData.inventory?.wall) ? updateData.inventory.wall.length : 0,
        };
        const tilesCount = Array.isArray(updateData.tiles) ? updateData.tiles.length : 0;
        console.log('Saving game data - counts => items:', invCounts.item, 'floor:', invCounts.floor, 'wall:', invCounts.wall, 'tiles:', tilesCount);

        gameDataModel.findOneAndUpdate(
            { user_id: userId },
            { $set: updateData },
            { new: true, upsert: true }
        )
            .then((result) => {
                console.log('Save successful for user:', userId);
                resolve(result);
            })
            .catch((error) => {
                console.error('Save failed with error:', error?.message || error);
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
                console.error('Sync error:', error?.message || error);
                reject(false);
            });
    });
}