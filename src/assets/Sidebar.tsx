import React, { useEffect, useState } from 'react';
import axios from 'axios';

type SidebarProps = {
  isOpen: boolean;
};

const Sidebar: React.FC<SidebarProps> = ({ isOpen }) => {
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

  return (
    <div
      className={`fixed top-16 left-0 h-screen w-60 bg-gray-900 text-white p-4 shadow-lg z-40 transform transition-transform duration-300 ${isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
    >
      {/* Render fetched queries */}
      {queries.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium text-gray-400">Recent Queries</h3>
          <ul className="mt-2 space-y-1 text-sm">
            {queries.map((query, index) => (
              <li key={index} className="truncate text-white">🔍 {query}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Sidebar;
