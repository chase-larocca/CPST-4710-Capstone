// Retrieve the cart from localStorage
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// Get references to HTML elements
const cartTable = document.getElementById('cart-items');
const orderTotalElement = document.getElementById('order-total');
const selectedAddressElement = document.querySelector('.order-total-box p');

let orderTotal = 0;

// Clear table content before populating
cartTable.innerHTML = '';

// Populate cart dynamically
cart.forEach((item, index) => {
  const row = document.createElement('tr');
  const imageUrl = productImageBaseUrl + item.SKU + ".png";  

  // Calculate customization charge
  const customizationCharge = (item.customization === 'Patriotic' ? 2 :
                               item.customization !== 'Customize' && item.customization !== '' ? 5 : 0);
  const itemTotal = (item.price + customizationCharge) * item.quantity;
  orderTotal += itemTotal;

  row.innerHTML = `
    <td class="product-info">
      
      <img src="${imageUrl}" alt="test" >
      ${item.name}
    </td>
    <td>${item.color}</td>
    <td>${item.customization}</td>
    <td>${item.quantity}</td>
    <td>$${itemTotal.toFixed(2)}</td>
    <td><button class="remove-btn" data-index="${index}">🗑️</button></td>
  `;

  cartTable.appendChild(row);
});

// Update order total display
orderTotalElement.textContent = `$${orderTotal.toFixed(2)}`;

// Handle item removal
document.addEventListener('click', function (e) {
  if (e.target.classList.contains('remove-btn')) {
    const index = e.target.dataset.index;
    cart.splice(index, 1);
    localStorage.setItem('cart', JSON.stringify(cart));
    location.reload(); 
  }
});

// Handle address selection dynamically
document.querySelectorAll('.shipping-selection select').forEach(select => {
  select.addEventListener('change', updateAddressDisplay);
});

function updateAddressDisplay() {
  const state = document.querySelector('.shipping-selection select:nth-child(1)').value;
  const city = document.querySelector('.shipping-selection select:nth-child(2)').value;
  const address = document.querySelector('.shipping-selection select:nth-child(3)').value;

  if (state !== 'Select Shipping State' && city !== 'Select Shipping City' && address !== 'Select Shipping Address') {
    selectedAddressElement.textContent = `${address}, ${city}, ${state}`;
  }
}

// Handle "Submit Order" button
document.querySelector('.submit-btn').addEventListener('click', () => {
  if (cart.length === 0) {
    alert("Your cart is empty. Please add items before submitting your order.");
    return;
  }

  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);

  console.log("Total Number of Items:", totalItems);

  const orderData = {
    items: cart,
    total: orderTotal,
    NumberOfItems: totalItems,
    shippingAddress: selectedAddressElement.textContent
  };

  console.log("Order Data:", orderData)

  fetch('/api/submit-order', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(orderData)
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert(`Order submitted successfully! Order Number: ${data.orderNumber}`);
      localStorage.removeItem('cart');
      window.location.href = '/order-status';
    } else {
      alert("Oops, something went wrong. Please try again.");
    }
  })
  .catch(() => {
    alert("Oops, something went wrong. Please try again.");
  });
});

// Handle "Shop More" button
document.querySelector('.shop-btn').addEventListener('click', () => {
  window.location.href = '/product';
});
