import React, { useState } from 'react'

const SignUp = () => {
  const [FirstName, setFirstName] = useState<string>("")
  const [SecondName, setSecondName] = useState<string>("")
  const [Email, setEmail] = useState<string>("")
  const [Password, setPassword] = useState<string>("")
  const [emailError, setEmailError] = useState<boolean>(false)
  const [passwordError, setPasswordError] = useState<boolean>(false)
  const [nameError, setnameError] = useState<boolean>(false)
  const handleFirstName = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFirstName(event.target.value)
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
    setEmail(event.target.value)
    if (Email.length > 0 && !validEmail(Email)) {
      setEmailError(true)
    }
    else {
      setEmailError(false)
    }
  }
  const handlepassword = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(event.target.value)
    if (Password.length > 0 && !validpassword(Password)) {
      setPasswordError(true)
    }
    else {
      setPasswordError(false)
    }
  }
  const validEmail = (email: string): boolean => {
    const emailRegex: RegExp = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  const validpassword = (password: string): boolean => {
    const passwordRegex: RegExp = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$/;
    return passwordRegex.test(password);
  }
  return (
    <div className='w-screen min-h-screen flex justify-center items-center bg-gradient-to-b from-gray-100 to-gray-700'>
      <div className='w-3/4 h-3/4 flex justify-start items-center shadow-2xl'>
        <div className='w-1/2 h-full'>
          <img
            src='https://img.freepik.com/vector-premium/hombre-trabajando-su-computadora_801395-340.jpg' // Local image
            alt='SignUp page'
            className='w-full h-full'
          />
        </div>
        <div className='w-1/2 h-full flex items-center justify-center flex-col p-4 space-y-3'>
          <div className='flex justify-end items-center space-x-1'>
            <p className='underline text-gray-700 text-sm ml-25'>Already a user?</p>
            <p className='underline cursor-pointer text-blue-700 text-sm'>SignIn</p>
          </div>
          <div className='w-64'>
            <label htmlFor='FirstName' className='block text-sm font-medium text-gray-700 mb-1'>FirstName</label>
            <input
              id='FirstName'
              type='name'
              value={FirstName}
              onChange={handleFirstName}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black ${nameError ? 'border-red-700' : 'border-gray-500'}`}
              placeholder='Enter your first name'
            ></input>
          </div>
          <div className='w-64'>
            <label htmlFor='SecondName' className='block text-sm font-medium text-gray-700 mb-1'>SecondName</label>
            <input
              id='SecondName'
              value={SecondName}
              onChange={handleSecondName}
              type='name'
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black ${nameError ? 'border-red-700' : 'border-gray-500'}`}
              placeholder='Enter your second name'
            ></input>
          </div>
          <div className="w-64">
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={Email}
              onChange={handleEmail}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black ${emailError ? 'border-red-700' : 'border-gray-500'}`}
              placeholder="Enter your email"
            />
          </div>
          <div className='w-64'>
            <label htmlFor='password' className='block text-sm font-medium text-gray-700 mb-1'>Password</label>
            <input
              id='password'
              type='password'
              value={Password}
              onChange={handlepassword}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black ${passwordError ? 'border-red-700' : 'border-gray-500'}`}
              placeholder='Enter your password'
            >
            </input>
          </div>
          <div className='w-64 flex items-center '>
            <p className='underline text-blue-700 text-sm cursor-pointer'>Forgot Password?</p>
          </div>
          <div className='w-64'>
              <button className='w-full'>SignUP</button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SignUp