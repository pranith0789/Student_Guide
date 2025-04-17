import React, { useState } from 'react';
import { Send } from '@mui/icons-material';
import axios from 'axios';

interface ResponseInfo {
  answer: string;
  sources: string[];
}

const Main: React.FC = () => {
  const [input, setInput] = useState<string>('');
  const [info, setInfo] = useState<ResponseInfo>({ answer: '', sources: [] });
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  const handleInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInput(event.target.value);
    setError('');
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    setIsLoading(true);
    setError('');
    setInfo({ answer: '', sources: [] });

    try {
      const response = await axios.post<{ answer: string; sources: string[] }>(
        'http://localhost:3000/search',
        { input }
      );
      console.log('Response:', response.data);
      setInfo({
        answer: response.data.answer || 'No answer returned',
        sources: response.data.sources || [],
      });
    } catch (err) {
      setError('Failed to fetch information. Please try again.');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    handleSend();
  };

  // Parse YouTube URLs and filter answer
  const youtubeUrls = info.sources.filter((source) =>
    source.includes('youtube.com/watch?v=')
  );
  const nonYoutubeSources = info.sources.filter(
    (source) => !source.includes('youtube.com/watch?v=')
  );
  // Remove YouTube section from answer (e.g., "YouTube Videos:\n...")
  const cleanedAnswer = info.answer.split('\n\nYouTube Videos:')[0].trim();

  // Extract video IDs for embedding
  const getVideoId = (url: string): string => {
    const match = url.match(/v=([^&]+)/);
    return match ? match[1] : '';
  };

  return (
    <div className="w-screen min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-blue-900 text-white flex flex-col items-center p-6">
      <div className="w-full max-w-3xl flex flex-col gap-6">
        {/* Title */}
        <h2 className="text-4xl font-extrabold text-center tracking-tight drop-shadow-lg animate-fade-in">
          What can I help with?
        </h2>

        {/* Response */}
        {info.answer && (
          <div className="p-4 bg-gray-800/80 rounded-xl shadow-md animate-fade-in">
            {/* Display cleaned answer (local DB or Stack Overflow) */}
            {cleanedAnswer && (
              <p className="text-lg whitespace-pre-wrap mb-4">{cleanedAnswer}</p>
            )}

            {/* YouTube Videos */}
            {youtubeUrls.length > 0 && (
              <div className="mb-4">
                <p className="text-sm font-semibold mb-2">YouTube Videos:</p>
                <div className="flex flex-col gap-4">
                  {youtubeUrls.map((url, index) => (
                    <div key={index} className="w-full">
                      <iframe
                        width="100%"
                        height="auto"
                        src={`https://www.youtube.com/embed/${getVideoId(url)}`}
                        title={`YouTube Video ${index + 1}`}
                        frameBorder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                        className="aspect-video rounded-md"
                      ></iframe>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Non-YouTube Sources */}
            {nonYoutubeSources.length > 0 && (
              <div>
                <p className="text-sm font-semibold">Sources:</p>
                <ul className="list-disc pl-5 text-sm">
                  {nonYoutubeSources.map((source, index) => (
                    <li key={index}>
                      <a
                        href={source}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:underline"
                      >
                        {source}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="p-4 bg-red-900/80 rounded-md shadow-md animate-fade-in">
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex flex-row w-full gap-3">
          <input
            type="text"
            placeholder="Ask me anything..."
            value={input}
            onChange={handleInput}
            disabled={isLoading}
            className="flex-1 p-4 rounded-xl bg-gray-700/90 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all duration-300 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
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
      </div>
    </div>
  );
};

export default Main;


