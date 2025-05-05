// import React, { useEffect, useState, useCallback, useRef } from 'react';
// import { Send } from '@mui/icons-material';
// import axios from 'axios';
// import ReactMarkdown from 'react-markdown';
// import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
// import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
// import type { Components } from 'react-markdown';
// import type { SyntaxHighlighterProps } from 'react-syntax-highlighter';

// interface ResponseInfo {
//   answer: string;
//   sources: string[];
// }

// const Main: React.FC = () => {
//   const [input, setInput] = useState<string>('');
//   const [response, setResponse] = useState<ResponseInfo | null>(null);
//   const [isLoading, setIsLoading] = useState<boolean>(false);
//   const [error, setError] = useState<string>('');
//   const [email, setEmail] = useState<string | null>(null);
//   const [showResponse, setShowResponse] = useState<boolean>(false);
//   const renderCount = useRef(0); // Track renders

//   //Load email from localStorage
//   // useEffect(() => {
//   //   const storedEmail = localStorage.getItem('userEmail');
//   //   console.log('Loaded email from localStorage:', storedEmail);
//   //   setEmail(storedEmail);
//   // }, []);

//   // // Persist info to localStorage
//   // useEffect(() => {
//   //   if (response && response.answer) {
//   //     localStorage.setItem('lastResponse', JSON.stringify(response));
//   //     console.log('Saved info to localStorage:', response);
//   //   }
//   // }, [response]);

//   // // Log renders
//   // useEffect(() => {
//   //   renderCount.current += 1;
//   //   console.log(`Render #${renderCount.current} with info:`, response);
//   // });

//   const handleInput = (event: React.ChangeEvent<HTMLInputElement>) => {
//     setInput(event.target.value);
//     setError('');
//   };

//   // Handle Enter key to prevent double submission
//   const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
//     if (event.key === 'Enter' && !isLoading) {
//       event.preventDefault();
//       handleSubmit(event as any);
//     }
//   };

//   const handleSend = useCallback(async () => {
//     if(!input.trim()){
//     //if (!input.trim() || !email) {
//       console.log('Invalid input or email:', { input, email });
//       setError('Please provide a valid input and ensure you are logged in.');
//       return;
//     }

//     setIsLoading(true);
//     setError('');
//     setShowResponse(false);
//     setResponse(null);

//     try {
//       console.log('Sending request to Node server:', { input});
//       const response = await axios.post<{ answer: string; sources: string[] }>(
//         'http://localhost:3000/search',
//         { input},
//         { headers: { 'Content-Type': 'application/json' }, timeout: 0 }
//       );

//       console.log('Response from Node server:', response.data);

//       if (response.data && typeof response.data.answer === 'string' && Array.isArray(response.data.sources)) {
//         const newResponse = {
//           answer: response.data.answer,
//           sources: response.data.sources,
//         };
//         console.log('Setting response:', newResponse);
//         setResponse(newResponse);
//         setInput('');
//         setShowResponse(true);
//       } else {
//         console.error('Invalid response structure:', response.data);
//         setError('Received invalid response format from server');
//       }
//     } catch (err) {
//       console.error('Error in handleSend:', err);
//       if (axios.isAxiosError(err)) {
//         console.error('Axios error details:', {
//           status: err.response?.status,
//           data: err.response?.data,
//           message: err.message,
//         });
//         setError(err.response?.data?.message || 'Failed to fetch information. Please try again.');
//       } else {
//         setError('An unexpected error occurred. Please try again.');
//       }
//     } finally {
//       setIsLoading(false);
//     }
//   }, [input, email]);

//   const handleSubmit = (event: React.MouseEvent) => {
//     event.preventDefault();
//     event.stopPropagation();
//     console.log('Button clicked with input:', input);
//     handleSend();
//   };

//   const youtubeUrls = response?.sources.filter((source) => source.includes('youtube.com/watch?v=')) || [];
//   const nonYoutubeSources = response?.sources.filter((source) => !source.includes('youtube.com/watch?v=')) || [];

//   const components: Components = {
//     code({ node, className, children, ...props }) {
//       const match = /language-(\w+)/.exec(className || '');
//       const syntaxHighlighterProps: SyntaxHighlighterProps = {
//         style: vscDarkPlus as any,
//         language: match?.[1] || 'text',
//         PreTag: 'div',
//         children: String(children).replace(/\n$/, ''),
//         ...props,
//       };
//       return match ? (
//         <SyntaxHighlighter {...syntaxHighlighterProps} />
//       ) : (
//         <code className={className} {...props}>
//           {children}
//         </code>
//       );
//     },
//     strong({ children }) {
//       return <strong className="font-bold">{children}</strong>;
//     },
//   };

//   return (
//     <div className="w-screen min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-blue-900 text-white flex flex-col items-center p-6">
//       <div className="w-full max-w-3xl flex flex-col gap-6">
//         <h2 className="text-4xl font-extrabold text-center tracking-tight drop-shadow-lg animate-fade-in">
//           What can I help with?
//         </h2>

//         {showResponse && response && !isLoading && (
//           <div className="p-4 bg-gray-800/80 rounded-xl shadow-md animate-fade-in">
//             <div className="prose prose-invert max-w-none">
//               <ReactMarkdown components={components} remarkPlugins={[]}>
//                 {response.answer}
//               </ReactMarkdown>
//             </div>
//             <div className="mt-2 text-xs text-gray-400">
//               <p>Answer length: {response.answer.length}</p>
//               <p>Number of sources: {response.sources.length}</p>
//             </div>
//             {youtubeUrls.length > 0 && (
//               <div className="mt-4">
//                 <p className="text-sm font-semibold mb-2">YouTube Videos:</p>
//                 <div className="flex flex-col gap-4">
//                   {youtubeUrls.map((url, index) => (
//                     <div key={index} className="w-full">
//                       <iframe
//                         width="100%"
//                         height="auto"
//                         src={`https://www.youtube.com/embed/${url.split('v=')[1]?.split('&')[0]}`}
//                         title={`YouTube Video ${index + 1}`}
//                         frameBorder="0"
//                         allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
//                         allowFullScreen
//                         className="aspect-video rounded-md"
//                       ></iframe>
//                     </div>
//                   ))}
//                 </div>
//               </div>
//             )}
//             {nonYoutubeSources.length > 0 && (
//               <div className="mt-4">
//                 <p className="text-sm font-semibold">Sources:</p>
//                 <ul className="list-disc pl-5 text-sm">
//                   {nonYoutubeSources.map((source, index) => (
//                     <li key={index}>
//                       {source.startsWith('http') ? (
//                         <a
//                           href={source}
//                           target="_blank"
//                           rel="noopener noreferrer"
//                           className="text-blue-400 hover:underline"
//                         >
//                           {source}
//                         </a>
//                       ) : (
//                         <span>{source}</span>
//                       )}
//                     </li>
//                   ))}
//                 </ul>
//               </div>
//             )}
//           </div>
//         )}

//         {isLoading && (
//           <div className="p-4 bg-gray-800/80 rounded-xl shadow-md animate-fade-in">
//             <div className="flex items-center justify-center">
//               <svg
//                 className="animate-spin h-8 w-8 text-blue-500"
//                 xmlns="http://www.w3.org/2000/svg"
//                 fill="none"
//                 viewBox="0 0 24 24"
//               >
//                 <circle
//                   className="opacity-25"
//                   cx="12"
//                   cy="12"
//                   r="10"
//                   stroke="currentColor"
//                   strokeWidth="4"
//                 ></circle>
//                 <path
//                   className="opacity-75"
//                   fill="currentColor"
//                   d="M4 12a8 8 0 018-8v8h8a8 8 0 01-16 0z"
//                 ></path>
//               </svg>
//             </div>
//           </div>
//         )}

//         {error && (
//           <div className="p-4 bg-red-900/80 rounded-md shadow-md animate-fade-in">
//             <p className="text-sm">{error}</p>
//           </div>
//         )}

//         <div className="flex flex-row w-full gap-3">
//           <input
//             type="text"
//             placeholder="Ask me anything..."
//             value={input}
//             onChange={handleInput}
//             onKeyPress={handleKeyPress}
//             //disabled={isLoading || !email}
//             className="flex-1 p-4 rounded-xl bg-gray-700/90 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all duration-300 disabled:opacity-50"
//             autoComplete="off"
//           />
//           <button
//             type="button"
//             onClick={handleSubmit}
//             disabled={!input.trim() || isLoading || !email}
//             className="p-4 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-500 rounded-xl flex items-center justify-center transition-all duration-200 shadow-lg hover:shadow-xl"
//             aria-label="Send message"
//           >
//             {isLoading ? (
//               <svg
//                 className="animate-spin h-5 w-5 text-white"
//                 xmlns="http://www.w3.org/2000/svg"
//                 fill="none"
//                 viewBox="0 0 24 24"
//               >
//                 <circle
//                   className="opacity-25"
//                   cx="12"
//                   cy="12"
//                   r="10"
//                   stroke="currentColor"
//                   strokeWidth="4"
//                 ></circle>
//                 <path
//                   className="opacity-75"
//                   fill="currentColor"
//                   d="M4 12a8 8 0 018-8v8h8a8 8 0 01-16 0z"
//                 ></path>
//               </svg>
//             ) : (
//               <Send className="text-white" />
//             )}
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Main;

import axios from "axios";
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import React from "react";

const Main = () => {
  const [input, setInput] = useState<string>("");
  const [response, setResponse] = useState<string>("");
  const [sources, setSources] = useState<string[]>([]);
  const [suggestion,setSuggestion] = useState<string>("");
  const {userId} = useParams()
  // Load saved data from localStorage on first render
  useEffect(() => {
    const savedInput = localStorage.getItem("lastInput");
    const savedResponse = localStorage.getItem("lastResponse");
    const savedSources = localStorage.getItem("lastSources");
    const savedSuggestion = localStorage.getItem("lastSuggestion")

    if (savedInput) setInput(savedInput);
    if (savedResponse) setResponse(savedResponse);
    if (savedSources) setSources(JSON.parse(savedSources));
    if(savedSuggestion) setSuggestion(savedSuggestion)
  }, []);

  // Sync state to localStorage on change
  useEffect(() => {
    localStorage.setItem("lastInput", input);
  }, [input]);

  useEffect(() => {
    if (response) {
      localStorage.setItem("lastResponse", response);
    }
  }, [response]);

  useEffect(() => {
    if (sources.length > 0) {
      localStorage.setItem("lastSources", JSON.stringify(sources));
    }
  }, [sources]);

  useEffect(()=>{
    if(suggestion){
      localStorage.setItem("lastSuggestion",suggestion)
    }
  },[suggestion])

  // Handle input change
  const handleInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInput(event.target.value);
  };

  // Handle form submission
  const handleSubmit = async (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();

    setResponse(""); // Clear old response in UI only
    setSources([]);  // Clear old sources in UI only

    try {
      const { data } = await axios.post<{ answer: string; sources: string[]; suggestion:string}>(
        "http://localhost:3000/search",
        { input,userId },
        {
          headers: { "Content-Type": "application/json" },
          timeout: 0,
        }
      );

      setResponse(data.answer);
      setSources(data.sources);
      setSuggestion(data.suggestion)
    } catch (err) {
      console.error("Error sending data", err);
      setResponse("❌ Failed to get response from server.");
    }
  };

  return (
    <div className="min-h-screen w-screen flex items-center justify-center bg-gray-800 p-4">
      <div className="bg-white rounded-2xl shadow-lg p-6 w-full max-w-3xl space-y-6">
        <div className="flex flex-col md:flex-row items-center gap-4">
          <input
            type="text"
            value={input}
            placeholder="Ask your question"
            onChange={handleInput}
            className="flex-1 px-4 py-2 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
          />
          <button
            onClick={handleSubmit}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-xl transition-all"
          >
            Enter
          </button>
        </div>

        {response && (
          <div className="bg-gray-100 p-4 rounded-xl text-gray-800 whitespace-pre-wrap">
            <strong>Response:</strong>
            <p className="mb-2">{response}</p>
            {sources.length > 0 && (
              <>
                <strong>Sources:</strong>
                <ul className="list-disc list-inside">
                  {sources.map((src, idx) => (
                    <li key={idx}>
                      {src.startsWith('http') ? (
                        <a href={src} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">{src}</a>
                      ) : (
                        src
                      )}
                    </li>
                  ))}
                </ul>
              </>
            )}
            <strong>Suggestion:</strong>
            <p className="mb-2">{suggestion}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Main;





