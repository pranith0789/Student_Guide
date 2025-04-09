import express from "express"
import mongoose from "mongoose"
import cors from "cors"
import axios from "axios"
import bcrypt from "bcryptjs"


const app = express()
app.use(cors())
app.use(express.json())

mongoose.connect("mongodb://localhost:27017/Accounts")
        .then(() => {
            console.log("DB Connected")
        }).catch((err) => { 
            console.log("Error connecting to Db:",err)
        });

const userschema = new mongoose.Schema({
    FirstName  : {type:String,required:true},
    LastName   : {type:String,required:true},
    Email      : {type:String,required:true,unique:true},
    Password   : {type:String,required:true},
});

const User = mongoose.model("User",userschema,"users")

app.post("/login",async(req,res) => {
    console.log("Received login information")
    
    const{email,password} = req.body
    try{
        const foundUser = await User.findOne({email})
        if(!foundUser){
            console.log("user not found")
            return res.status(400).json({message:"user not found"})
        }
        const isvalidpassword = await bcrypt.compare(Password,foundUser.Password)
        if(!isvalidpassword){
            console.log("Incorrect Password")
            return res.status(401).json({message:"Incorrect Password"})
        }
        console.log("user logged in:",foundUser.email);
        return res.status(200).json({message:"User logged in successfully"})
    }catch(err){
        console.log("Error logging in:",err)
        return res.status(500).json({message:"Error logging in user"})
    }
})

app.listen(3000, () => console.log("server is running on port 3000"));