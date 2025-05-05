import axios from 'axios'
import { ChangeEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
const Login = () => {
  const[Email,setEmail] = useState<string>("")
  const[password,setPassword] = useState<string>("")
  const[emailError,setEmailError] = useState<string>("")
  const[passwordError,setPasswordError] = useState<string>("")
  const[error,setError] = useState<string>("")
  const navigate = useNavigate()
  const handlemail = (event: ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setEmail(value);
    setEmailError(value.length > 0 && !validEmail(value) ? "Invalid Email" : "");
  };
  
  const handlepassword = (event: ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setPassword(value);
    setPasswordError(value.length > 0 && !validpassword(value) ? "Invalid password" : "");
  };
  
  const validEmail = (email:string): boolean =>{
    const emailRegex: RegExp = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  const validpassword = (password:string): boolean => {
    const passwordRegex: RegExp = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$/;
    return passwordRegex.test(password);
  }

  const handlenaviagte = () => {
    navigate("/SignUp")
  }

  const handlelogin = async (event: React.FormEvent) => {
    event.preventDefault()
    if(!Email.trim() || !password.trim()){
      setError("Enter valid credentials")
      return;
    }
    try{
      const response = await axios.post('http://localhost:3000/login',{Email,password})
      console.log("Login Successfull",response.data)
      if (response.data && response.data.email && response.data.user_id) {
        console.log('Storing email in localStorage:', response.data.email);
        localStorage.setItem('userEmail', response.data.email);
        localStorage.setItem('userID',response.data.user_id)
        navigate("/Main")
      } else {
        console.error('Invalid response format from login:', response.data);
        setError("Login failed: Invalid response from server");
      }
    }catch(Error){
      console.error("Login failed", Error);
      setError("Login failed. Please check your credentials and try again.");
    }
  }

  return (
    <div className='w-screen min h-screen bg-gradient-to-b from-purple-400 to-indigo-400 items-center justify-center flex'>
        <div className='h-3/4 w-3/4 bg-white shadow-2xl/30 shadow-stone-700 relative flex items-center'>
          <div className="w-1/2 h-3/4 bg-white rounded-lg shadow-xl/30 shadow-gray-500 ml-10">
            <div className="flex justify-center items-center flex-col p-4 space-y-4">
              <h1 className="font-bold text-gray-700">Login</h1>
              <div className="flex space-x-2">
                <p className="underline text-black text-sm">Doesn't have an account yet?</p>
                <p className="underline text-blue-600 cursor-pointer text-sm" onClick={handlenaviagte}>Signup</p>
              </div>
              <div className="w-64">
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  value={Email}
                  onChange={handlemail}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black ${emailError ? 'border-red-600' : 'border-gray-300'}`}                 
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
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black ${passwordError ? 'border-red-600' : 'border-gray-300'}`}
                  placeholder="Enter your password"
                />
              </div>
              <div className='w-64'>
                <button
                  className={`w-full mt-5 py-2 rounded-md font-semibold text-white ${
                    error || emailError || passwordError || !Email || !password
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-blue-600 hover:bg-blue-700'
                  }`}
                  disabled={!!emailError || !!passwordError || !Email || !password}
                  onClick={handlelogin}
                >
                  Login
                </button>
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


