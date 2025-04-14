import React, { useState } from 'react';
import { Send } from '@mui/icons-material';
import axios from 'axios';

const Main = () => {
  const [input, setInput] = useState<string>('');
  const [info, setInfo] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  const handleInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInput(event.target.value);
    setError(''); // Clear error on new input
  };

  const handleSend = async () => {
    if (!input.trim()) return; // Prevent empty submissions
    setIsLoading(true);
    setError('');
    setInfo('');

    try {
      const response = await axios.post('http://localhost:3000/search', { input });
      setInfo(response.data || 'No information returned');
    } catch (err) {
      setError('Failed to fetch information. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault(); // Prevent form refresh
    handleSend();
  };

  return (
    <div className="w-screen h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-blue-900 text-white flex flex-col justify-center items-center p-6">
      <h2 className="text-4xl font-extrabold mb-8 text-center tracking-tight drop-shadow-lg animate-fade-in">
        What can I help with?
      </h2>
      <form onSubmit={handleSubmit} className="flex flex-row w-full max-w-3xl gap-3">
        <input
          type="text"
          placeholder="Ask me anything..."
          value={input}
          onChange={handleInput}
          disabled={isLoading} // Disable input during loading
          className="flex-1 p-4 rounded-xl bg-gray-700/90 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all duration-300 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={!input.trim() || isLoading} // Disable if empty or loading
          className="p-4 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-500 rounded-xl flex items-center justify-center transition-all duration-200 shadow-lg hover:shadow-xl"
          aria-label="Send message"
        >
          {isLoading ? (
            <svg
              className="animate-spin h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v8h8a8 8 0 01-16 0z"
              ></path>
            </svg>
          ) : (
            <Send className="text-white" />
          )}
        </button>
      </form>

      {/* Display response or error */}
      <div className="w-full max-w-3xl mt-6">
        {info && (
          <div className="p-4 bg-gray-800/80 rounded-xl shadow-md animate-fade-in">
            <p className="text-lg">{info}</p>
          </div>
        )}
        {error && (
          <div className="p-4 bg-red-900/80 rounded-md shadow-md animate-fade-in">
            <p className="text-sm">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Main;