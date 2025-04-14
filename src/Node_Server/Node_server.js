import express from "express"
import mongoose from "mongoose"
import cors from "cors"
import axios from "axios"
import bcrypt from "bcryptjs"


const app = express()
app.use(cors())
app.use(express.json())

mongoose.connect("mongodb://localhost:27017/Users")
        .then(() => {
            console.log("DB Connected")
        }).catch((err) => { 
            console.log("Error connecting to Db:",err)
        });

const userschema = new mongoose.Schema({
    FirstName  : {type:String,required:true},
    LastName   : {type:String,required:true},
    Email      : {type:String,required:true,unique:true},
    password   : {type:String,required:true},
});

const User = mongoose.model("User",userschema,"Users")

app.post("/login",async(req,res) => {
    console.log("Received login information")
    
    const{Email,password} = req.body
    try{
        const foundUser = await User.findOne({Email})
        if(!foundUser){
            console.log("user not found")
            return res.status(400).json({message:"user not found"})
        }
        const isvalidpassword = await bcrypt.compare(password,foundUser.password)
        if(!isvalidpassword){
            console.log("Incorrect Password")
            return res.status(401).json({message:"Incorrect Password"})
        }
        console.log("user logged in:",foundUser?.Email);
        return res.status(200).json({message:"User logged in successfully"})
    }catch(err){
        console.log("Error logging in:",err)
        return res.status(500).json({message:"Error logging in user"})
    }
})

app.post("/Register",async(req,res) => {
    console.log("Received registration request",req.body)
    const{FirstName,LastName,Email,password}=req.body
    try{
        const excistingUser = await User.findOne({Email})
        if(excistingUser){
            console.log("User already exist",Email)
            return res.status(400).json({message:"User already exist"})
        }
        const hashedPassword = await bcrypt.hash(password,10)
        const newUser = new User({FirstName,LastName,Email,password:hashedPassword})
        await newUser.save()

        console.log("User registered:",newUser)
        return res.status(201).json({message:"User created"})
    }catch(err){
        console.log("Can't create a user",err)
        return  res.status(500).json({message:"Can't create a user"})
    }
})


app.post("/search",async(req,res) => {
    console.log("Received search request",req.body)
    const{input}=req.body
    if(!input || !input.trim()){
        console.log("Invalid input received")
        return res.status(400).json({message:'Input is required'})
    }
    try{
        const fastapiresponse = await axios.post('http://localhost:8000/rag',{prompt:input},{timeout : 10000})
        const responsedata = fastapiresponse.data;
        console.log('FastAPI response',responsedata);
    }catch(err){
        console.log('Error contacting server',err)
        return res.status(500).json({message:'Error processing search request'})

    }
})

app.listen(3000, () => console.log("server is running on port 3000"));