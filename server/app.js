//load the environment variables
require('dotenv').config();

//dependencies
const express = require('express');
const cors = require('cors');
const app = express();
const mongoose = require('mongoose');
const routes = require('./routes/routes');

const PORT = 8000;
const URI = "mongodb+srv://Thysis:[REMOVED]@room-designer-cluster.fut1o6k.mongodb.net/?retryWrites=true&w=majority&appName=Room-Designer-Cluster";

//middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(cors());
app.use(routes);

app.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok' });
});

//connect to database
mongoose.connect(URI)
    .then(() => {
        console.log("Successfully connected to DB!");

        //start server
        const server = app.listen(PORT, (error) => {
            if (error) {
                console.log(`Server initialization on port http://localhost:${PORT} failed.`);
            } else {
                console.log(`Server is running on port http://localhost:${PORT}.`);
            }
        });
        // Disable default 2-minute timeout; let client control timeouts
        server.setTimeout(0);
    })
    .catch(error => {
        console.error("Failed to connect to DB: ", error)
        process.exit(1);
    });