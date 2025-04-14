import React,{useState} from 'react'

const Main = () => {
  const[input,setInput] = useState<string>("");
  
  const handleInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInput(event.target.value)
  }

  return (
    <div className='w-screen h-screen bg-gray-900 text-white flex flex-col justify-center items-center p-6'>
      <h2 className='text-3xl font-semibold mb-6 text-center'>
        What can I help with?
      </h2>
      <input
        type='text'
        placeholder='Ask me anything...'
        value={input}
        onChange={handleInput}
        className='w-full max-w-xl p-4 rounded-xl bg-gray-800 text-white placeholder-gray-400'
      />
    </div>
  )
}

export default Main
