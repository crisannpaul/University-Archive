import Hero from "../components/Hero";
import Navbar from "../components/Navbar";

function Home (){
    return(
        <>
        <Navbar />
            <Hero 
            cName = "hero"
            
            title = "All cool with Al-CooL"
            text = "Let us surprise you"
            buttonText = "Check our offer"
            url="/menu"
            btnClass = "show"
            />
            

        </>
    );
}
export default Home;