

const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Submission = sequelize.define('Submission', {
    id: { type: DataTypes.INTEGER, autoIncrement: true, primaryKey: true },
    team_id: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
            model: 'teams', // lowercase plural
            key: 'id'
        },
           onDelete: "CASCADE",
      onUpdate: "CASCADE",
    },
    problem_id: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
            model: 'problems', // lowercase plural
            key: 'id'
        },
           onDelete: "CASCADE",
      onUpdate: "CASCADE",
    },
    event_id: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
            model: 'events', // lowercase plural
            key: 'id'
        },
           onDelete: "CASCADE",
      onUpdate: "CASCADE",
    },
    code: { type: DataTypes.TEXT, allowNull: false },
    language: { type: DataTypes.STRING, allowNull: false },
    failed_test_case: {
        type: DataTypes.TEXT,
        defaultValue: null,
        allowNull: true
    },
    result: {
        type: DataTypes.TEXT,
        allowNull: false,
        defaultValue: 'Pending'
    },
     execution_time: {
        type: DataTypes.FLOAT,
        defaultValue: 0.0
    },
      memory_usage: {
        type: DataTypes.FLOAT,
        defaultValue: 0.0
    },
     submitted_at: {
        type: DataTypes.DATE,
        defaultValue: DataTypes.NOW
    },
    verdict: { type: DataTypes.STRING, allowNull: true },
    created_at: { type: DataTypes.DATE, allowNull: true, defaultValue: DataTypes.NOW }
}, {
    timestamps: false
});

module.exports = Submission;