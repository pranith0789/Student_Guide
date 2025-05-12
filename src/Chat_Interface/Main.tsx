import axios from "axios";
import { useState, useEffect } from "react";
import React from "react";
import Navbar from "../assets/Navbar";
import Sidebar from "../assets/Sidebar";

const Main = () => {
  const [input, setInput] = useState<string>("");
  const [response, setResponse] = useState<string>("");
  const [sources, setSources] = useState<string[]>([]);
  const [suggestion, setSuggestion] = useState<string>("");
  const [userId, setUserId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);
  const [isNewchat, setisNewChat] = useState<boolean>(false)
  


  useEffect(() => {
    const savedInput = localStorage.getItem("lastInput");
    const savedResponse = localStorage.getItem("lastResponse");
    const savedSources = localStorage.getItem("lastSources");
    const savedSuggestion = localStorage.getItem("lastSuggestion");
    const savedUserId = localStorage.getItem("userID");
    if (savedInput) setInput(savedInput);
    if (savedResponse) setResponse(savedResponse);
    if (savedSources) setSources(JSON.parse(savedSources));
    if (savedSuggestion) setSuggestion(savedSuggestion);
    setUserId(savedUserId);
  }, []);

  useEffect(() => {
    localStorage.setItem("lastInput", input);
  }, [input]);

  useEffect(() => {
    if (response) localStorage.setItem("lastResponse", response);
  }, [response]);

  useEffect(() => {
    if (sources.length > 0) {
      localStorage.setItem("lastSources", JSON.stringify(sources));
    }
  }, [sources]);

  useEffect(() => {
    if (suggestion) {
      localStorage.setItem("lastSuggestion", suggestion);
    }
  }, [suggestion]);

  const handleInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInput(event.target.value);
  };

  const handleSubmit = async (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    setResponse("");
    setSources([]);

    try {
      const { data } = await axios.post<{
        answer: string;
        sources: string[];
        suggestion: string;
      }>("http://localhost:3000/search", { input, userId });

      setResponse(data.answer);
      setSources(data.sources);
      setSuggestion(data.suggestion);
    } catch (err) {
      console.error("Error sending data", err);
      setResponse("❌ Failed to get response from server.");
    }
  };

  return (
    <div className="min-h-screen w-screen bg-gray-800">
      <Navbar setSidebarOpen={setSidebarOpen} onNewChat={() => {
                  setisNewChat(true);
                  setInput("");
                  setResponse("");
                  setSources([]);
                  setSuggestion("");
      }}/>
      <div className="flex pt-16">
        {sidebarOpen && <Sidebar isOpen={sidebarOpen}
        onQuerySelect = {(query:string, response:string) => {
          setInput(query)
          setResponse(response)
          setSources([])
          setSuggestion("")
        }}
        />}

        <div
          className={`transition-all duration-300 p-4 w-full ${
            sidebarOpen ? "ml-40" : "ml-0"
          }`}
        >
          <div className="bg-white rounded-2xl shadow-lg p-6 max-w-3xl mx-auto space-y-6 mt-6">
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
                          {src.startsWith("http") ? (
                            <a
                              href={src}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 underline"
                            >
                              {src}
                            </a>
                          ) : (
                            src
                          )}
                        </li>
                      ))}
                    </ul>
                  </>
                )}
                {suggestion && suggestion.trim() && (
                  <>
                    <strong>Suggestion:</strong>
                    <p className="mb-2">{suggestion}</p>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Main;
