import React from "react";
import MenuIcon from "@mui/icons-material/Menu";

type NavbarProps = {
  setSidebarOpen: React.Dispatch<React.SetStateAction<boolean>>;
};

const Navbar: React.FC<NavbarProps> = ({ setSidebarOpen }) => {
  return (
    <div className="w-full h-16 flex items-center bg-gray-700 fixed top-0 left-0 z-50 px-4">
      <button
        onClick={() => setSidebarOpen((prev) => !prev)}
        className="flex justify-start h-full items-center text-white p-2 hover:bg-gray-600 hover:rounded-full transition-all"
      >
        <MenuIcon />
      </button>
    </div>
  );
};

export default Navbar;
