import express from "express";
import mongoose from "mongoose";
import cors from "cors";
import axios from "axios";
import bcrypt from "bcryptjs";

const app = express();
app.use(cors());
app.use(express.json());

mongoose
  .connect("mongodb://localhost:27017/Users")
  .then(() => console.log("DB Connected"))
  .catch((err) => console.log("Error connecting to DB:", err));

const userSchema = new mongoose.Schema({
  FirstName: { type: String, required: true },
  LastName: { type: String, required: true },
  Email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
});

const User = mongoose.model("User", userSchema, "Users");

app.post("/login", async (req, res) => {
  console.log("Received login request:", req.body);
  const { Email, password } = req.body;
  try {
    const foundUser = await User.findOne({ Email });
    if (!foundUser) {
      console.log("User not found:", Email);
      return res.status(400).json({ message: "User not found" });
    }
    const isValidPassword = await bcrypt.compare(password, foundUser.password);
    if (!isValidPassword) {
      console.log("Incorrect Password for:", Email);
      return res.status(401).json({ message: "Incorrect Password" });
    }
    console.log("User logged in:", foundUser.Email);
    return res.status(200).json({ message: "User logged in successfully", email: foundUser.Email });
  } catch (err) {
    console.error("Error logging in:", err);
    return res.status(500).json({ message: "Error logging in user" });
  }
});

app.post("/Register", async (req, res) => {
  console.log("Received registration request:", req.body);
  const { FirstName, LastName, Email, password } = req.body;
  try {
    const existingUser = await User.findOne({ Email });
    if (existingUser) {
      console.log("User already exists:", Email);
      return res.status(400).json({ message: "User already exists" });
    }
    const hashedPassword = await bcrypt.hash(password, 10);
    const newUser = new User({ FirstName, LastName, Email, password: hashedPassword });
    await newUser.save();
    console.log("User registered:", newUser.Email);
    return res.status(201).json({ message: "User created" });
  } catch (err) {
    console.error("Error creating user:", err);
    return res.status(500).json({ message: "Can't create a user" });
  }
});

app.post("/search", async (req, res) => {
  console.log("Received search request:", req.body);
  const { input} = req.body;

  if (!input || !input.trim()) {
    console.log("Invalid input received");
    return res.status(400).json({
      answer: "Please provide a valid input",
      sources: [],
    });
  }

  try {
    // const user = await User.findOne({ Email: email });
    // if (!user) {
    //   console.log("User not found for email:", email);
    //   return res.status(401).json({
    //     answer: "User not found. Please login again.",
    //     sources: [],
    //   });
    // }

    // console.log("Forwarding request to FastAPI with user_id:", user._id.toString());
    const fastapiResponse = await axios.post("http://localhost:8000/query", {
      prompt: input,
      // user_id: user._id.toString(),
    });

    console.log("FastAPI response received:", fastapiResponse.data);

    // Validate response structure
    if (!fastapiResponse.data || typeof fastapiResponse.data.answer !== "string" || !Array.isArray(fastapiResponse.data.sources)) {
      console.error("Invalid FastAPI response structure:", fastapiResponse.data);
      return res.status(500).json({
        answer: "Invalid response from AI server",
        sources: [],
      });
    }

    const formattedResponse = {
      answer: fastapiResponse.data.answer,
      sources: fastapiResponse.data.sources,
    };

    console.log("Sending formatted response to frontend:", formattedResponse);
    return res.status(200).json(formattedResponse);
  } catch (err) {
    console.error("Error in search endpoint:", err);
    return res.status(500).json({
      answer: "Sorry, I encountered an error while processing your request. Please try again.",
      sources: [],
    });
  }
});

app.listen(3000, () => console.log("Server is running on port 3000"));