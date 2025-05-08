import axios from 'axios'
import { ChangeEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [Email, setEmail] = useState<string>("")
  const [password, setPassword] = useState<string>("")
  const [emailError, setEmailError] = useState<string>("")
  const [passwordError, setPasswordError] = useState<string>("")
  const [error, setError] = useState<string>("")
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

  const validEmail = (email: string): boolean => {
    const emailRegex: RegExp = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  const validpassword = (password: string): boolean => {
    const passwordRegex: RegExp = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$/;
    return passwordRegex.test(password);
  }

  const handlenaviagte = () => {
    navigate("/SignUp")
  }

  const handlelogin = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!Email.trim() || !password.trim()) {
      setError("Enter valid credentials")
      return;
    }
    try {
      const response = await axios.post('http://localhost:3000/login', { Email, password })
      if (response.data && response.data.email && response.data.user_id) {
        localStorage.setItem('userEmail', response.data.email);
        localStorage.setItem('userID', response.data.user_id)
        navigate("/Main")
      } else {
        setError("Login failed: Invalid response from server");
      }
    } catch (Error) {
      console.error("Login failed", Error);
      setError("Login failed. Please check your credentials and try again.");
    }
  }

  return (
    <div className='w-screen min-h-screen bg-gradient-to-b from-purple-400 to-indigo-400 flex items-center justify-center px-4 py-8'>
      <div className='bg-white rounded-xl shadow-lg flex flex-col lg:flex-row w-full max-w-5xl'>
        {/* Form Section */}
        <div className='w-full lg:w-1/2 p-6 md:p-10 flex flex-col justify-center'>
          <h1 className="text-2xl font-bold text-gray-700 text-center mb-6">Login</h1>
          <div className="flex justify-center items-center mb-6 text-sm">
            <p className="text-black mr-1">Don't have an account?</p>
            <p className="text-blue-600 underline cursor-pointer" onClick={handlenaviagte}>Signup</p>
          </div>
          <form onSubmit={handlelogin} className="flex flex-col space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                id="email"
                type="email"
                value={Email}
                onChange={handlemail}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black ${emailError ? 'border-red-600' : 'border-gray-300'}`}
                placeholder="Enter your email"
              />
            </div>
            <div>
              <div className="flex justify-between items-center mb-1">
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">Password</label>
                <p className="text-sm text-blue-600 underline cursor-pointer">Forgot Password?</p>
              </div>
              <input
                id="password"
                type="password"
                value={password}
                onChange={handlepassword}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black ${passwordError ? 'border-red-600' : 'border-gray-300'}`}
                placeholder="Enter your password"
              />
            </div>
            {error && <p className="text-red-600 text-sm">{error}</p>}
            <button
              type="submit"
              disabled={!!emailError || !!passwordError || !Email || !password}
              className={`w-full py-2 rounded-md font-semibold text-white ${
                error || emailError || passwordError || !Email || !password
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              Login
            </button>
          </form>
        </div>

        {/* Image Section */}
        <div className="w-full lg:w-1/2">
          <img
            src="https://res.cloudinary.com/zaphyrpro/image/upload/v1691614400/blog/creating-opportunities/engaging-with-people-who-want-to-push-you-forward.webp"
            alt="background"
            className="w-full h-full object-cover rounded-b-xl lg:rounded-r-xl lg:rounded-bl-none"
          />
        </div>
      </div>
    </div>
  );
}

export default Login;
