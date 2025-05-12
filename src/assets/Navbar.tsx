import React, { useEffect, useState } from "react";
import MenuIcon from "@mui/icons-material/Menu";
import VideoLabelIcon from "@mui/icons-material/VideoLabel";
import ExitToAppIcon from "@mui/icons-material/ExitToApp";
import { useNavigate } from "react-router-dom";


type NavbarProps = {
  setSidebarOpen: React.Dispatch<React.SetStateAction<boolean>>;
  onNewChat : () => void 
};


const Navbar: React.FC<NavbarProps> = ({ setSidebarOpen,onNewChat }) => {
  const [userID,setUserId] = useState<string>('')
  useEffect(()=>{
    const saveduserid = localStorage.getItem("userID")
    if(saveduserid){
      setUserId(saveduserid)
    }
  },[])
  const navigate = useNavigate()
  const handleexitfunction = () => {
    localStorage.clear()
    navigate('/')
  }
  const handlecleanup = () => {
      localStorage.clear()
      if(userID){
        localStorage.setItem("userID",userID)
      }
      console.log(userID)
      onNewChat();
  }
  return (
    <div className="w-full h-16 bg-gray-700 fixed top-0 left-0 z-50 px-4 flex items-center">
      {/* Left Section */}
      <div className="flex-1 flex items-center">
        <button
          onClick={() => setSidebarOpen((prev) => !prev)}
          className="text-white p-2 hover:bg-gray-600 hover:rounded-full transition-all"
        >
          <MenuIcon />
        </button>
      </div>

      {/* Right Section */}
      <div className="flex-1 flex justify-end items-center gap-7 text-white">
        <div
          onClick={handlecleanup}
          className="p-2 hover:bg-gray-900 rounded-full transition duration-300 ease-in-out cursor-pointer">
          <VideoLabelIcon />
        </div>
        <div
          onClick={handleexitfunction}
          className="p-2 hover:bg-gray-900 rounded-full transition duration-300 ease-in-out cursor-pointer">
          <ExitToAppIcon/>
        </div>
      </div>
    </div>
  );
};

export default Navbar;
