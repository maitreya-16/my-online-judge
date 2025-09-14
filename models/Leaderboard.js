// models/Leaderboard.js
const { DataTypes } = require("sequelize");
const sequelize = require("../config/database");

const Leaderboard = sequelize.define("Leaderboard", {
  id: {
    type: DataTypes.INTEGER,
    autoIncrement: true,
    primaryKey: true,
  },

  event_id: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: { model: "events", key: "id" },
    onDelete: "CASCADE",
  },

  team_id: {
    type: DataTypes.INTEGER,
    allowNull: false,
    // references: { model: "teams", key: "id" },
    // onDelete: "CASCADE",
  },

  // Array of objects: [{ problem_id, score, accepted_time }]
  problem_1: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
  },
  problem_2: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
  },
  problem_3: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
  },
  problem_4: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
  },
  problem_5: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
  },

  total_score: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
  },

  total_solved: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
  },

  last_submission_time: {
    type: DataTypes.DATE,
    allowNull: true,
  },

}, {
  indexes: [
    {
      unique: true,
      fields: ["event_id", "team_id"], // ensures unique team per event
    },
  ],
  timestamps: true, // adds createdAt & updatedAt
});

module.exports = Leaderboard;
