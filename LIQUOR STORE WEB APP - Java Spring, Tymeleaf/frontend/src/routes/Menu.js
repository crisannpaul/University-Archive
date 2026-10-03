import Hero from "../components/Hero";
import Navbar from "../components/Navbar";
import MainContent from "../components/mainContent";

function Menu (){
    return(
        <>
        <Navbar />
        <div className="content"><MainContent /></div>
        
        </>
    )
}
export default Menu;