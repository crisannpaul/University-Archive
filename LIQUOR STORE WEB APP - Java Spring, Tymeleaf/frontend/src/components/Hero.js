
import "./HeroStyles.css";

function Hero (props){
    return(
        <>
        <div className={props.cName}> 
            <img className="image1" src = "https://images.squarespace-cdn.com/content/v1/58ab01a41b631b5940750784/1581335512363-Z5FZOEIQ9OW9KN151O6V/nwbLiquorStore0158.jpg"/>
        <div className="hero-text">
            <h1>{props.title}</h1>
            <p>{props.text}</p>
            <a href={props.url} className={props.btnClass}>
                Discover our offer
            </a>
        
        </div>

        </div>
        
        </>
    );
}
export default Hero;