const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const { User, Team } = require("../models");
require("dotenv").config();
const Event = require("../models/Event");
exports.registerUser = async (req, res) => {
    try {
        console.log(req.body); // Debug incoming request body
        const { username, email, password, isjunior, event_id ,role} = req.body;

        // Input validation
        if (!username || !email || !password || isjunior === undefined ) {
            return res.status(400).json({ error: 'All fields are required' });
        }

        if (role !== 'admin' && !event_id) {
            return res.status(400).json({ error: 'Event ID is required for non-admin users' });
        }

        if (typeof password !== 'string' || password.length < 6) {
            return res.status(400).json({ error: 'Password must be a string and at least 6 characters long' });
        }

        const event = await Event.findByPk(event_id);
        if (!event) {
            return res.status(400).json({ error: 'Event not found' });
        }

        // Email format validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            return res.status(400).json({ error: 'Invalid email format' });
        }

        // Username format validation
        if (username.length < 3 || username.length > 20) {
            return res.status(400).json({ error: 'Username must be between 3 and 20 characters' });
        }

        const checkUser = await User.findOne({ where: { username, event_id } });
        if (checkUser) {
            return res.status(400).json({ error: 'Username already exists for this event and category' });
        }

        const checkEmail = await User.findOne({ where: { email, event_id } });
        if (checkEmail) {
            return res.status(400).json({ error: 'Email already registered' });
        }

        const hashedPassword = await bcrypt.hash(password, 10);

        //  First, create the user
        const newUser = await User.create({
            username,
            password: hashedPassword,
            email,
            role: role || 'user',
            isjunior,
            event_id
        });

        //  Now, create their solo team using their user ID
        const soloTeam = await Team.create({
            team_name: `${username}_solo_${event_id}`,
            user1_id: newUser.id,  // Assign the user ID after creation
            user2_id: null,        // No second user
            event_id,
            isjunior,
            score: 0
        });

        //  Update the user with their solo team ID
        await newUser.update({ team_id: soloTeam.id });
        await soloTeam.update({ user1_id: newUser.id });

        res.status(201).json({ 
            message: 'User registered successfully!', 
            user: {
                username: newUser.username,
                email: newUser.email,
                event_id: newUser.event_id,
                isjunior: newUser.isjunior
            }
        });

    } catch (error) {
        console.error('Registration error:', error);
        if (error.name === 'SequelizeValidationError') {
            return res.status(400).json({ 
                error: 'Validation error', 
                details: error.errors.map(e => e.message)
            });
        }
        res.status(500).json({ error: 'Error registering user', details: error.message });
    }
};
exports.RegisterTeam = async (req, res) => {
    try {
        const { username1, team_name, username2, event_id} = req.body;

        //  Find both users
        const user1 = await User.findOne({ where: { username: username1, event_id } });
        const user2 = await User.findOne({ where: { username: username2, event_id } });

        const event = await Event.findByPk(event_id);
        if (!event) {
            return res.status(400).json({ error: 'Event not found' });
        }

        if (!user1 || !user2) {
            return res.status(404).json({ error: "Both users must be registered before creating a team." });
        }

        //  Ensure both users are in solo teams (i.e., user2_id must be NULL)
        const soloTeam1 = await Team.findOne({ where: { id: user1.team_id, user2_id: null } });
        const soloTeam2 = await Team.findOne({ where: { id: user2.team_id, user2_id: null } });

        if (!soloTeam1 || !soloTeam2) {
            return res.status(400).json({ error: "Both users must be playing solo before forming a team." });
        }

        //  Ensure users belong to the same event & category
        if (user1.event_id !== user2.event_id || user1.isjunior !== user2.isjunior) {
            return res.status(400).json({ error: "Both users must be in the same event and category." });
        }

        const teamExists = await Team.findOne({ where: { team_name, event_id } });
        if (teamExists) {
            return res.status(400).json({ error: "Team name already exists. Please choose another." });
        }

        const team = await Team.create({
            team_name,
            user1_id: user1.id,
            user2_id: user2.id,
            event_id,
            isjunior: user1.isjunior,
            score: 0
        });

        //  Delete their old solo teams
        await Team.destroy({ where: { id: user1.team_id } });
        await Team.destroy({ where: { id: user2.team_id } });

        //  Assign the new team ID to both users
        await User.update({ team_id: team.id }, { where: { id: user1.id } });
        await User.update({ team_id: team.id }, { where: { id: user2.id } });

        return res.status(201).json({ message: "Team registered successfully!", team: team.team_name });
    }
    catch (error) {
        console.error("Error registering team:", error);
        return res.status(500).json({ error: "Error registering team", details: error.message });
    }
};

exports.Login = async (req, res) => {
    try {
        const { username, password, event_id ,isjunior} = req.body;

        // Input validation
        if (!username || !password || !event_id) {
            return res.status(400).json({ error: 'Username, password, and event_id are required' });
        }

        const event = await Event.findByPk(event_id);
        if (!event) {
            return res.status(400).json({ error: 'Event not found' });
        }

        const now = new Date();
        if (!event.start_time || now < event.start_time) {
            return res.status(403).json({ error: "Event has not started yet" });
        }
        if (now > event.end_time) {
            return res.status(403).json({ error: "Event has ended" });
        }
        let user;

            user = await User.findOne({ where: { username } });

            if(user.isjunior!=isjunior){
                return res.status(404).json({ error: "User not found" });
            }

            if (!user || (event_id === 1 && user.ncc===null) || (event_id===2 && user.rc===null)) {
                return res.status(404).json({ error: "User not found. Please register first" });
            }


        const validPassword = await bcrypt.compare(password, user.password);

        if (!validPassword) {
            return res.status(401).json({ error: "Invalid username or password" });
        }

        const token = jwt.sign(
            {
                id: user.id,
                username: user.username,
                event_id: event_id,
                isjunior: user.isjunior,
                team_id: event_id===1?user.ncc:user.rc
            },
            process.env.JWT_SECRET,
            { expiresIn: "2h" }
        );

        // Get cookie settings from environment variables
        const domain = process.env.COOKIE_DOMAIN || 'localhost';
        const isSecure = process.env.COOKIE_SECURE === 'true';
        const sameSite = process.env.COOKIE_SAME_SITE || 'Lax';

        console.log('Cookie settings:', {
            domain,
            isSecure,
            sameSite,
            frontendUrl: process.env.FRONTEND_URL
        });

        res.cookie("token", token, {
            httpOnly: true,    // Prevents JavaScript access
            secure: isSecure,  // Set via environment variable
            sameSite: sameSite, // Set via environment variable
            domain: domain,    // Set domain based on environment
            path: '/',         // Cookie available for all paths
            maxAge: 2 * 60 * 60 * 1000, // 2 hours
            credentials: 'include' // Required for cross-origin requests
        });

        console.log('Response headers:', res.getHeaders());
        return res.status(200).json({
            message: "User logged in successfully",
            user: {
                username: user.username,
                event_id: user.event_id,
                isjunior: user.isjunior,
            }
        });

    } catch (error) {
        console.error("Error logging in:", error);
        res.status(500).json({ error: "Error logging in", details: error.message });
    }
};
exports.GetProfile = async(req,res)=>{
    try{
        const user = await User.findByPk(req.user.id,{attributes:{exclude:['password']}});
        return res.status(200).json({user});
    }catch(error){
        console.error("Error fetching user profile:", error);
        res.status(500).json({ error: "Error fetching user profile", details: error.message });
    }
};

exports.Logout = async (req,res)=>{
    try{
        res.clearCookie("token");
        res.status(200).json({message:"User logged out successfully"});
    }
    catch(error){
        console.error("Error logging out:", error);
        res.status(500).json({ error: "Error logging out", details: error.message });
    }
};

exports.getAllEvents = async (req, res) => {
    try {
        const events = await Event.findAll();
        const now = new Date();
        
        for (const event of events) {
            if (event.end_time && now > event.end_time) {
                event.is_active = false;
                await event.save();
            }
        }
        res.status(200).json({ events });
    } catch (error) {
        res.status(500).json({ error: 'Error fetching events', details: error.message });
    }
};

