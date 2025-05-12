import React, { useEffect, useState } from 'react';
import axios from 'axios';

type SidebarProps = {
  isOpen: boolean;
  onQuerySelect : (query:string, response: string) => void 
};

const Sidebar: React.FC<SidebarProps> = ({ isOpen,onQuerySelect }) => {
  const [userID, setUserId] = useState<string | null>(null);
  const [queries, setQueries] = useState<string[]>([]);

  useEffect(() => {
    const savedUserId = localStorage.getItem("userID");
    if (savedUserId) {
      setUserId(savedUserId);
    }
  }, []);

  useEffect(() => {
    const fetchQueries = async () => {
      if (!userID) {
        console.log("No userID available yet");
        return;
      }

      try {
        console.log("Fetching queries for userID:", userID);
        const { data } = await axios.post<{ Queries: string[] }>(
          "http://localhost:3000/user_query",
          { userId: userID }
        );
        console.log("Fetched Queries:", data);
        setQueries(data.Queries);
      } catch (error) {
        console.error("Failed to fetch queries:", error);
      }
    };

    fetchQueries();
  }, [userID]);

  const handleQuerySelect = async (query:string) => {
    try{
      const {data} = await axios.post<{response:string}>(
        "http://localhost:3000/query_response",
        {
          query:query,
          userID : userID
        }
      )
        if(data.response){
          onQuerySelect(query,data.response)
  
        }else{
          console.error("No response found for query")
        }
    }
    
    catch(error){
      console.error("Error fetching query response:query")
    }
  }

  return (
    <div
      className={`fixed top-16 left-0 h-[calc(100vh-4rem)] w-60 bg-gray-900 text-white p-4 shadow-lg z-40 transform transition-transform duration-300 overflow-y-auto ${isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
    >
      {/* Render fetched queries */}
      {queries.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium text-gray-400">Recent Queries</h3>
          <ul className="mt-2 space-y-1 text-sm">
            {queries.map((query, index) => (
              <li
                key={index}
                onClick={() => handleQuerySelect(query)}
                className="truncate text-white mb-5 px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg shadow-sm transition duration-200"
              >
                🔍 {query}
              </li>
            ))}
            
          </ul>
        </div>
      )}
    </div>
  );
};

export default Sidebar;
