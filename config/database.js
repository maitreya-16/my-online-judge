const { Sequelize } = require('sequelize');
const dotenv = require('dotenv').config();


// import { Sequelize } from 'sequelize';
// import fs from 'fs';
const fs = require('fs');
// import dotenv from 'dotenv';


const DB_HOST = "34.93.234.239";
const DB_USER = "postgres";
const DB_PASS = "Postgres25@";
const DB_NAME = "rcdb";
const DB_PORT = 5432;
const DB_DIALECT = 'postgres';
console.log(DB_PASS);
console.log(DB_HOST);
console.log(DB_USER);
console.log(DB_NAME);
console.log(DB_PORT);

const sequelize = new Sequelize(
  DB_NAME,
  DB_USER,
  DB_PASS,
  {
    host: DB_HOST,
    port: DB_PORT,
    dialect: DB_DIALECT,
    dialectOptions: {
      ssl: {
        require: true,
        rejectUnauthorized: false,
        ca: fs.readFileSync('./certs/server-ca.pem').toString(),
        key: fs.readFileSync('./certs/client-key.pem').toString(),
        cert: fs.readFileSync('./certs/client-cert.pem').toString(),
      },
    },
    logging: false,
  }
);

// export default sequelize;
// const sequelize = new Sequelize(process.env.DB_URL, {
//   dialect: 'postgres',
//   protocol: 'postgres',
//   logging: false,
//   define: {
//     timestamps: true,
//     underscored: true,
//   },
// });

// Test connection function
const testDBConnection = async () => {
  try {
    console.log(DB_PASS);
    await sequelize.authenticate();
    console.log(`✅ Connected to ${DB_DIALECT} database at ${DB_HOST}:${DB_PORT}`);
    return true;
  } catch (error) {
    console.error('❌ Unable to connect to the database:', error);
    return false;
  }
};

// Export the sequelize instance as default export
module.exports = sequelize;

// Export test function separately if needed
module.exports.testDBConnection = testDBConnection;

