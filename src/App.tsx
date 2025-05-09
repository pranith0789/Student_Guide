import Login from "./Authentication_Pages/Login"
import SignUp from "./Authentication_Pages/SignUp"
import {BrowserRouter,Routes,Route} from 'react-router-dom'
import WelcomePage from "./Welcome_Page/WelcomePage"
import Main from "./Chat_Interface/Main"
function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<WelcomePage/>}/>
          <Route path="/Login" element={<Login/>}/>
          <Route path="/SignUp" element={<SignUp/>}/>
          <Route path="/Main" element={<Main/>}/>
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App
