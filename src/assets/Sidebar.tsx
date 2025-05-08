import React, { useEffect } from 'react';

type SidebarProps = {
  isOpen: boolean;
};

useEffect(()=>{
    
})

const Sidebar: React.FC<SidebarProps> = ({ isOpen }) => {
  return (
    <div
      className={`fixed top-16 left-0 h-screen w-60 bg-gray-900 text-white p-4 shadow-lg z-40 transform transition-transform duration-300 ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      <h2 className="text-lg font-semibold">Sidebar</h2>
      <ul className="mt-4 space-y-2">
        <li>🏠 Home</li>
        <li>📄 Docs</li>
        <li>⚙️ Settings</li>
      </ul>
    </div>
  );
};

export default Sidebar;
