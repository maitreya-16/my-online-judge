const express = require("express");
require("dotenv").config();
const http = require("http");
// const cors = require("cors");
const sequelize = require("./config/database");
const { syncDB } = require('./models');
const cookieParser = require('cookie-parser');
const { initSocket } = require('./SocketConnection');
const adminRoutes = require('./routes/adminRoutes');
const userRoutes = require('./routes/userRoutes');
const problemroutes = require('./routes/problemroutes');
const resultRoutes = require('./routes/resultRoutes');
const leaderboardRoutes = require('./routes/leaderboardroutes');
const submissionRoutes = require('./routes/submissionRoutes');
const webhookRoutes = require('./routes/WebhookRoutes');
const app = express();
app.use(express.json());  // To handle JSON payloads
app.use(cookieParser())
//const PORT = process.env.PORT || 5000;
const cors = require("cors");

// CORS configuration
const allowedOrigins = process.env.ALLOWED_ORIGINS 
? process.env.ALLOWED_ORIGINS.split(',') 
: ["http://localhost:5173", "http://localhost:3000"];

// Allow all origins
app.use(cors({
    origin: "*",
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"]
}));

const server = http.createServer(app);
(async () => {
    await syncDB();
})();
// Routes
app.get("/", (req, res) => res.send("🚀 Online Judge API is running..."));
app.use("/admin", adminRoutes);
app.use("/user", userRoutes);
app.use("/problems", problemroutes);
app.use("/result", resultRoutes);
app.use("/leaderboard", leaderboardRoutes);
app.use("/submission",submissionRoutes);
app.use("/webhook",webhookRoutes);
const PORT = process.env.PORT || 3000;

sequelize.sync()
  .then(() => {
    console.log("✅ Database connected & synced");

    initSocket(server, {
      cors: {
        origin: "*",
        credentials: true,
      },
    });

    app.listen(PORT, () => {
      console.log(`🚀 Server running at http://localhost:${PORT}`);
    });
  })
  .catch((err) => {
    console.error("❌ Failed to connect DB:", err);
  });
