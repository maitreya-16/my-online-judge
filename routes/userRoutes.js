const express = require('express');
require("dotenv").config();
const userController = require("../controllers/userController");
const router = express.Router();

const auth = require('../middlewares/authMiddleware')

// router.post("/register", userController.registerUser);
router.post("/login", userController.Login);
router.post("/logout", auth, userController.Logout);
// router.post("/register-team", userController.RegisterTeam);
router.get('/profile', auth, userController.GetProfile);
module.exports = router;

