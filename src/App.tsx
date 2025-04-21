import Login from "./Authentication_Pages/Login"
import SignUp from "./Authentication_Pages/SignUp"
import {BrowserRouter,Routes,Route} from 'react-router-dom'
import Main from "./AI_Agent/Main"
function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/Login" element={<Login/>}/>
          <Route path="/SignUp" element={<SignUp/>}/>
          <Route path="/Main" element={<Main/>}/>
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App
