import TextField from '@mui/material/TextField';
const Login = () => {
  return (
    <div className='w-screen min h-screen bg-gradient-to-b from-purple-400 to-indigo-400 items-center justify-center flex'>
        <div className='h-3/4 w-3/4 bg-white shadow-2xl shadow-stone-700 relative flex items-center'>
          <div className="w-1/2 h-3/4 bg-white rounded-lg shadow-xl ml-10">
            <div className="flex justify-center items-center flex-col p-4 space-y-4">
              <h1 className="font-bold text-gray-700">Login</h1>
              <div className="flex space-x-2">
                <p className="underline text-black">Doesn't have an account yet?</p>
                <p className="underline text-blue-600 cursor-pointer">Signup</p>
              </div>
              <TextField
                id="outlined-search"
                label="Email"
                type="search"
                className="mb-4 w-64"
              />
              <br></br>
              <TextField
                id="outlined-password-input"
                label="Password"
                type="password"
                autoComplete="current-password"
                className="mt-4 w-64"
              />
            </div>
          </div>
        </div>
    </div>
  )
}

export default Login