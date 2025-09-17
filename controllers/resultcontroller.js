const Leaderboard  = require("../models/Leaderboard.js");

/**
 * Get result (rank + stats) for a particular team in an event
 */
exports.getTeamResult = async (req, res) => {
  try {
    const event_id = req.user.event_id 
    const team_id = req.user.team_id
    // Fetch all teams for this event in sorted order
    const leaderboard = await Leaderboard.findAll({
      where: { event_id },
      order: [
        ["total_score", "DESC"],
        ["last_submission_time", "ASC"], // tie-breaker
      ],

    });

    if (!leaderboard.length) {
      return res.status(404).json({ message: "No leaderboard data for this event." });
    }

    // Find the rank + entry for this team
    let teamResult = null;
    let rank = null;

    leaderboard.forEach((entry, index) => {
      if (entry.team_id === parseInt(team_id)) {
        teamResult = entry;
        rank = index + 1; // rank starts at 1
      }
    });

    if (!teamResult) {
      return res.status(404).json({ message: "Team not found in this event." });
    }

    // Build response
    return res.status(200).json({
      event_id,
      team_id: teamResult.team_id,
      team_name: teamResult.Team?.team_name,
      rank,
      total_score: teamResult.total_score,
      total_solved: teamResult.total_solved,
      last_submission_time: teamResult.last_submission_time,
      problems: teamResult.problems, // [{ problem_id, score, accepted_time }]
    });
  } catch (error) {
    console.error("Error fetching team result:", error);
    return res.status(500).json({ message: "Server error", error: error.message });
  }
};
