const express = require('express');
const router = express.Router();
const submissionController = require('../controllers/submissionController');
const auth = require('../middlewares/authMiddleware');

router.post('/run',auth,submissionController.RunProblem);

router.post('/run-system',auth,submissionController.RunOnSystem);

router.post('/submit',auth,submissionController.SubmitProblem);

module.exports = router;