fetch('/api/products')
.then(response => response.json())

.then(data => {
  const container = document.querySelector('.product-grid'); 
  container.innerHTML = '';

  data.forEach(product => {
    const card = document.createElement('div');
    card.classList.add('product-card');

    card.innerHTML = `
  <img src="https://placehold.co/150x150" alt="Product" class="product-image" />
  <div class="product-details">
    <div class="product-title-price">
      <span class="product-name">${product.ItemName}</span>
      <span class="separator">|</span>
      <span class="product-price">$${parseFloat(product.Price).toFixed(2)}</span>
    </div>
    <div class="customization-row">
      <select class="color-select">
        ${(product.Colors ?? []).map(c => `<option>${c}</option>`).join('')}
      </select>
      <select class="customization-select">
        <option value="">Customize</option>
        <option>Air Force</option>
        <option>Marines</option>
        <option>Army</option>
        <option>Coast Guard</option>
        <option>Space Force</option>
        <option>National Guard</option>
        <option>Navy</option>
        <option>Patriotic</option>
      </select>
      <input type="number" placeholder="QTY" class="qty-field" />
    </div>
    <button class="add-to-cart-btn">Add to Cart</button>
  </div>
`;

    container.appendChild(card);
  });
})
.catch(error => console.error("Error fetching products:", error));

// Load cart from localStorage or start with empty array
let cart = JSON.parse(localStorage.getItem('cart')) || [];

document.addEventListener('click', function (event) {
    if (event.target.classList.contains('add-to-cart-btn')) {
      const card = event.target.closest('.product-card');
  
      const name = card.querySelector('.product-name')?.textContent;
      const price = parseFloat(card.querySelector('.product-price')?.textContent.replace('$', '') || 0);
      const color = card.querySelector('.color-select')?.value;
      const customization = card.querySelector('.customization-select')?.value;
      const quantity = parseInt(card.querySelector('.qty-field')?.value || 0);
  
      if (!quantity || quantity <= 0) {
        alert("Please enter a valid quantity.");
        return;
      }

      const item = {
        name,
        price,
        color,
        customization,
        quantity
      };
  
      cart.push(item);
      localStorage.setItem('cart', JSON.stringify(cart));
  
      alert(`${quantity} of "${name}" added to cart!`);
      console.log(JSON.parse(localStorage.getItem('cart')));
    }
  });
  
