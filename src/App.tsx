import Login from "./Authentication_Pages/Login"
import SignUp from "./Authentication_Pages/SignUp"
import {BrowserRouter,Routes,Route} from 'react-router-dom'
function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/Login" element={<Login/>}/>
          <Route path="/SignUp" element={<SignUp/>}/>
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App
