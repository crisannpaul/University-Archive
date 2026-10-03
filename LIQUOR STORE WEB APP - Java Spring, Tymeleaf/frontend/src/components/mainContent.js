import React from 'react'
import product_card from "../assets/product_data";
import './mainContent.css';

const MainContent = () => {
    console.log(product_card);
    const listItems = product_card.map((item) =>
        <div className="card" key={item.id}>
            <div className="card_img">
                <img className="image1" src = "https://purepng.com/public/uploads/large/purepng.com-wine-bottlebottle-food-wine-object-alcohol-beverage-cocktail-liquor-whiskey-drunk-941524623252xmmwk.png"/>
            </div>
            <div className="card_header">
                <h2>{item.product_name}</h2>
                <p>{item.description}</p>
                <p className="price">{item.price}<span>{item.currency}</span></p>
                <div className="btn">Add to cart</div>
            </div>
        </div>

    );
    return (
        <div className="main_content">
            {listItems}
        </div>
    )
}
export default MainContent;