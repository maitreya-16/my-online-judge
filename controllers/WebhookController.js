const { getIO } = require('../SocketConnection');

exports.RunWebhook = async (req, res) => {
  try {
    const { submission_id, status, message, user_output } = req.body;

    if (!submission_id || !status) {
      console.warn("[RunWebhook] Missing required fields:", req.body);
      return res.status(400).json({ error: "submission_id and status are required" });
    }

    console.info(`[RunWebhook] Submission: ${submission_id}, Status: ${status}`);
    if (status !== "executed_successfully") {
      console.warn(`[RunWebhook] Message: ${message || "No message provided"}`);
    }

    getIO().to(String(submission_id)).emit("result", {
      type: "run",
      submission_id,
      status,
      message,
      user_output,
      timestamp: new Date().toISOString(),
    });

    return res.status(200).json({ success: true, message: "Run webhook processed successfully" });
  } catch (error) {
    console.error("[RunWebhook] Error processing webhook:", error);
    return res.status(500).json({ error: "Internal server error" });
  }
};

exports.SystemWebhook = async (req, res) => {
    try {
        const { submission_id, status, message, expected_output } = req.body;

        console.log(`System Webhook for ${submission_id} — ${status}`);
        if (status !== "executed_successfully") console.log(`Message: ${message}`);

        getIO().to(String(submission_id)).emit('result', {
            type: 'system',
            submission_id,
            status,
            message,
            expected_output
        })

        res.status(200).json({ message: "System webhook processed successfully." });
    } catch (error) {
        console.error("Error processing system webhook:", error);
        res.status(500).json({ message: "Internal server error." });
    }
};