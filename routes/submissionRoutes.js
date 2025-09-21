const express = require('express');
const router = express.Router();
const submissionController = require('../controllers/submissionController');
const validateSubmissionWindow = require('../middlewares/validateSubmission.js');
const auth = require('../middlewares/authMiddleware');

router.post('/run',auth,validateSubmissionWindow,submissionController.RunProblem);

router.post('/run-system',auth,validateSubmissionWindow,submissionController.RunOnSystem);

router.post('/submit',auth,validateSubmissionWindow,submissionController.SubmitProblem);

module.exports = router;