
const { Leaderboard, Team, Problem } = require("../models");

/**
 * Update leaderboard when a submission is accepted
 * - Add/update problem entry
 * - Recalculate total_score, total_solved
 * - Update last_submission_time
 */
exports.updateLeaderboard = async (req, res) => {
  try {
    const { team_id, event_id, problem_id, verdict, submitted_at } = req.body;

    if (verdict !== "Accepted") {
      return res.status(200).json({ message: "No update (submission not accepted)" });
    }

    // Get problem score
    const problem = await Problem.findByPk(problem_id);
    if (!problem) {
      return res.status(404).json({ message: "Problem not found" });
    }

    // Find or create leaderboard entry
    let leaderboard = await Leaderboard.findOne({ where: { team_id, event_id } });
    if (!leaderboard) {
      leaderboard = await Leaderboard.create({
        team_id,
        event_id,
        problems: [],
        total_score: 0,
        total_solved: 0,
      });
    }

    let problems = leaderboard.problems || [];

    // Check if problem already solved
    const existing = problems.find((p) => p.problem_id === problem_id);

    if (!existing) {
      // Add new solved problem
      problems.push({
        problem_id,
        score: problem.score,
        accepted_time: submitted_at || new Date(),
      });

      leaderboard.total_score += problem.score;
      leaderboard.total_solved += 1;

      // Update last submission time (latest accepted)
      leaderboard.last_submission_time = submitted_at || new Date();

      leaderboard.problems = problems;
      await leaderboard.save();
    }

    return res.status(200).json({ message: "Leaderboard updated", leaderboard });
  } catch (error) {
    console.error("Error updating leaderboard:", error);
    return res.status(500).json({ message: "Server error", error: error.message });
  }
};

/**
 * Get leaderboard for an event
 * - Sorted by total_score (desc), then last_submission_time (asc)
 */
exports.getLeaderboard = async (req, res) => {
  try {
    // const { event_id } = req.params;
    const event_id = req.user.event_id;
    const isjunior = req.user.isjunior
    const leaderboard = await Leaderboard.findAll({
      where: { event_id ,isjunior},
      order: [
        ["total_score", "DESC"],
        ["last_submission_time", "ASC"], // tie-breaker
      ],
    });
    return res.status(200).json(leaderboard);
  } catch (error) {
    console.error("Error fetching leaderboard:", error);
    return res.status(500).json({ message: "Server error", error: error.message });
  }
};
