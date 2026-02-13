const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const User = sequelize.define('User', {
  id: {
    type: DataTypes.INTEGER,
    autoIncrement: true,
    primaryKey: true,
  },
  username: {
    type: DataTypes.STRING(255),
    allowNull: true,
  },
  teamname:{
    type: DataTypes.STRING(255),
    defaultValue:"TEAM",
    allowNull:false
  },
  name: {
    type: DataTypes.STRING(255),
    allowNull: true,
  },
  phone: {
    type: DataTypes.BIGINT,
    allowNull: true,
  },
  email: {
    type: DataTypes.STRING(255),
    allowNull: true,
    validate: { isEmail: true },
  },
  password: {
    type: DataTypes.STRING(255),
    allowNull: true,
  },
  rc: {
    type: DataTypes.INTEGER,
    allowNull: true,
  },
  isjunior: {
    type: DataTypes.BOOLEAN,
    allowNull: false,
    defaultValue: false,
  },
}, {
  tableName: 'user', // 👈 lowercase to avoid quoted "User"
  timestamps: false,
});

module.exports = User;
