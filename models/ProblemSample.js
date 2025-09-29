

const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const ProblemSample = sequelize.define('ProblemSample', {
    id: { type: DataTypes.INTEGER, autoIncrement: true, primaryKey: true },
    problem_id: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
            model: 'Problems', // lowercase plural
            key: 'id'
        }
    },
    input: { type: DataTypes.TEXT, allowNull: false },
    output: { type: DataTypes.TEXT, allowNull: false },
    explanation: { type: DataTypes.TEXT, allowNull: true }
}, {
    timestamps: false
});

module.exports = ProblemSample;
