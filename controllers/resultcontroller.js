const Leaderboard = require("../models/Leaderboard.js");
const sequelize = require("../config/database.js");
/**
 * Get result (rank + stats) for a particular team in an event
 */
exports.getTeamResult = async (req, res) => {
  try {
    const event_id = req.user.event_id
    const team_id = req.user.team_id
    const isjunior = req.user.isjunior
    if (!event_id || !team_id) {
      return res.status(400).json({ message: "Missing event_id or team_id in user data." });
    }

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

    const rows = await sequelize.query(`
  SELECT SUM(score) AS total_score
  FROM problems
  WHERE event_id = :event_id
    AND isjunior = :isjunior;
`, {
      replacements: { event_id, isjunior },
      type: sequelize.QueryTypes.SELECT
    });

    console.log(rows); // just the sum

    const totalpossiblescore = rows[0].total_score || 0;

    // Calculate accuracy
    const accuracy = totalpossiblescore > 0 ? (teamResult.total_score / totalpossiblescore) * 100 : 0;

    // Build response
    return res.status(200).json({
      username1: teamResult.username1,
      username2: teamResult.username2,
      isjunior: teamResult.isjunior,
      rank: rank,
      total_score: teamResult.total_score,
      total_submissions: teamResult.total_submissions,
      accuracy: `${Math.round(accuracy).toFixed(2)}%`,
    });
  } catch (error) {
    console.error("Error fetching team result:", error);
    return res.status(500).json({ message: "Server error", error: error.message });
  }
};
