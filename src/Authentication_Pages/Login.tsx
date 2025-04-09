import TextField from '@mui/material/TextField';
import { ChangeEvent, useState } from 'react';
const Login = () => {
  const[email,setEmail] = useState<string>("")
  const[password,setPassword] = useState<string>("")
  const[emailError,setEmailError] = useState<string>("")
  const[passwordError,setPasswordError] = useState<string>("")
  const[rememberMe,setRememberMe] = useState<boolean>(false)
  
  const handlemail = (event: ChangeEvent<HTMLInputElement>) => {
    setEmail(event.target.value)
    if(email.length>0 && !validEmail(email)){
      setEmailError("Invalid Email")
    }
    else{
      setEmailError("")
    }
  }

  const handlepassword = (event: ChangeEvent<HTMLInputElement>) =>{
    setPassword(event.target.value)
    if(password.length>0 && !validpassword(password)){
      setPasswordError("Invalid password")
    }
    else{
      setPasswordError("")
    }
  }

  const validEmail = (email:string): boolean =>{
    const emailRegex: RegExp = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  const validpassword = (password:string): boolean => {
    const passwordRegex: RegExp = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$/;
    return passwordRegex.test(password);
  }

  const handleRememberMe = (event: ChangeEvent<HTMLInputElement>) => {
    setRememberMe(event.target.checked);
  };

  return (
    <div className='w-screen min h-screen bg-gradient-to-b from-purple-400 to-indigo-400 items-center justify-center flex'>
        <div className='h-3/4 w-3/4 bg-white shadow-2xl/30 shadow-stone-700 relative flex items-center'>
          <div className="w-1/2 h-3/4 bg-white rounded-lg shadow-xl/30 shadow-gray-500 ml-10">
            <div className="flex justify-center items-center flex-col p-4 space-y-4">
              <h1 className="font-bold text-gray-700">Login</h1>
              <div className="flex space-x-2">
                <p className="underline text-black text-sm">Doesn't have an account yet?</p>
                <p className="underline text-blue-600 cursor-pointer text-sm">Signup</p>
              </div>
              <div className="w-64">
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={handlemail}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black ${emailError ? 'border-red-500' : 'border-gray-300'}`}                 
                  placeholder="Enter your email"
                />
              </div>
              <div className="w-64">
                <div className='flex flex-row justify-between items-center'>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                    Password
                  </label>
                  <p className='underline text-sm text-blue-600 cursor-pointer mb-1'>Forgot Password?</p>
                </div>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={handlepassword}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black ${passwordError ? 'border-red-500' : 'border-gray-300'}`}
                  placeholder="Enter your password"
                />
              </div>
              <div className='w-64'>
                <button className='w-full mt-5'>Login</button>
              </div>
            </div>
          </div>
          <div>
            <img src='https://res.cloudinary.com/zaphyrpro/image/upload/v1691614400/blog/creating-opportunities/engaging-with-people-who-want-to-push-you-forward.webp' alt='background-image'/>
          </div>
        </div>
    </div>
  );
}

export default Login;


