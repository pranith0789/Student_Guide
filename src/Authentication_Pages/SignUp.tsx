import React, { useEffect, useState } from 'react'
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
const SignUp = () => {
  const [FirstName, setFirstName] = useState<string>("")
  const [LastName, setSecondName] = useState<string>("")
  const [Email, setEmail] = useState<string>("")
  const [password, setPassword] = useState<string>("")
  const [emailError, setEmailError] = useState<boolean>(false)
  const [passwordError, setPasswordError] = useState<boolean>(false)
  const [nameError, setnameError] = useState<boolean>(false)
  const [Error, setError] = useState<string>("")
  const [success, setSuccess] = useState<string>("")
  const [registrationSuccess, setRegistrationSuccess] = useState<boolean>(false)
  const navigate = useNavigate()

  useEffect(() => {
    if (registrationSuccess) {
      const timer = setTimeout(() => {
        navigate("/Login")
      }, 2000);
      return () => clearTimeout(timer)
    }
  }, [registrationSuccess, navigate])

  const handleFirstName = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value
    setFirstName(value)
  }

  const handleSecondName = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newSecondName = event.target.value;
    setSecondName(newSecondName);
    if (FirstName === newSecondName) {
      setnameError(true);
    }
    else {
      setnameError(false);
    }
  }

  const handleEmail = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value
    setEmail(value)
    setEmailError(value.length > 0 && !validEmail(value))
  }

  const handlepassword = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value
    setPassword(value)
    setPasswordError(value.length > 0 && !validpassword(value))
  }

  const validEmail = (email: string): boolean => {
    const emailRegex: RegExp = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  const validpassword = (password: string): boolean => {
    const passwordRegex: RegExp = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$/;
    return passwordRegex.test(password);
  }

  const handlenavigate = () => {
    navigate("/Login")
  }
  const handleSignUp = async (event: React.FormEvent) => {
    event.preventDefault();

    // Final validation before allowing signup
    if (!Email || !password || emailError || passwordError || nameError) {
      setError("Please fill in valid credentials");
    }

    setError("");

    try {
      const response = await axios.post('http://localhost:3000/Register', {
        FirstName,
        LastName,
        Email,
        password,
      });
      console.log("User registered", response.data);
      if (response.status == 201) {
        setSuccess("User successfully created.")
        setRegistrationSuccess(true)
      }
    } catch (err) {
      console.log("User not registered", err);
      setError("Registration failed. Please try again.");
    }
  };
  return (
  <div className='w-screen min-h-screen flex justify-center items-center bg-gradient-to-b from-gray-100 to-gray-700 px-4 py-6'>
    <div className='w-full max-w-4xl flex flex-col md:flex-row justify-center items-center shadow-2xl bg-white rounded-lg overflow-hidden'>
      {/* Image Section */}
      <div className='w-full md:w-1/2 h-64 md:h-full'>
        <img
          src='https://img.freepik.com/vector-premium/hombre-trabajando-su-computadora_801395-340.jpg'
          alt='SignUp page'
          className='w-full h-full object-cover'
        />
      </div>

      {/* Form Section */}
      <div className='w-full md:w-1/2 h-full flex items-center justify-center flex-col p-6 space-y-3'>
        <div className='flex justify-end items-center space-x-1 self-end text-sm'>
          <p className='underline text-gray-700'>Already a user?</p>
          <p className='underline cursor-pointer text-blue-700' onClick={handlenavigate}>SignIn</p>
        </div>

        <div className='w-full max-w-xs'>
          <label htmlFor='FirstName' className='block text-sm font-medium text-gray-700 mb-1'>FirstName</label>
          <input
            id='FirstName'
            type='text'
            value={FirstName}
            onChange={handleFirstName}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black ${nameError ? 'border-red-700' : 'border-gray-500'}`}
            placeholder='Enter your first name'
          />
        </div>

        <div className='w-full max-w-xs'>
          <label htmlFor='SecondName' className='block text-sm font-medium text-gray-700 mb-1'>SecondName</label>
          <input
            id='SecondName'
            value={LastName}
            onChange={handleSecondName}
            type='text'
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black ${nameError ? 'border-red-700' : 'border-gray-500'}`}
            placeholder='Enter your second name'
          />
        </div>

        <div className="w-full max-w-xs">
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            id="email"
            type="email"
            value={Email}
            onChange={handleEmail}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black ${emailError ? 'border-red-700' : 'border-gray-500'}`}
            placeholder="Enter your email"
          />
        </div>

        <div className='w-full max-w-xs'>
          <label htmlFor='password' className='block text-sm font-medium text-gray-700 mb-1'>Password</label>
          <input
            id='password'
            type='password'
            value={password}
            onChange={handlepassword}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black ${passwordError ? 'border-red-700' : 'border-gray-500'}`}
            placeholder='Enter your password'
          />
        </div>

        <div className='w-full max-w-xs flex items-center'>
          <p className='underline text-blue-900 text-sm cursor-pointer'>Forgot Password?</p>
        </div>

        <div className='w-full max-w-xs'>
          <button
            className={`w-full mt-5 py-2 rounded-md font-semibold text-white ${Error || emailError || passwordError || !Email || !password
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700'
              }`}
            disabled={!!emailError || !!passwordError || !Email || !password}
            onClick={handleSignUp}>
            SignUp
          </button>
        </div>

        <div className='w-full max-w-xs flex justify-center'>
          {Error && <p className='text-red-500 text-sm font-medium'>{Error}</p>}
          {success && <p className='text-emerald-600 text-sm font-medium px-4 py-2 rounded-md'>{success}</p>}
        </div>
      </div>
    </div>
  </div>
  )
  }

  export default SignUp;