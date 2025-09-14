
const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const User = sequelize.define('User', {
    id: { type: DataTypes.INTEGER, autoIncrement: true, primaryKey: true },
    username: { type: DataTypes.STRING, allowNull: false },
    password: { type: DataTypes.STRING, allowNull: false, validate: { notEmpty: true } },
    email: { type: DataTypes.STRING, allowNull: false, validate: { isEmail: true } },
    role: { type: DataTypes.ENUM('user', 'admin'), defaultValue: 'user' },
    is_junior: { type: DataTypes.BOOLEAN, allowNull: false, defaultValue: false },
    event_id: {
        type: DataTypes.INTEGER,
        allowNull: true,
        references: {
            model: 'events', // lowercase plural
            key: 'id'
        },
           onDelete: "CASCADE",
      onUpdate: "CASCADE",
    },
    team_id: {
        type: DataTypes.INTEGER,
        allowNull: true,
    //     references: {
    //         model: 'teams', // lowercase plural
    //         key: 'id'
    //     },
    //        onDelete: "CASCADE",
    //   onUpdate: "CASCADE",
        
    },

    created_at: { type: DataTypes.DATE, allowNull: true, defaultValue: DataTypes.NOW }
}, {
    timestamps: false,
    indexes: [
        { unique: true, fields: ['username', 'event_id'] },
        { unique: true, fields: ['email', 'event_id'] }
    ]
});

module.exports = User;
