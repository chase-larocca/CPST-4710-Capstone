// Get the cart from localStorage
const cart = JSON.parse(localStorage.getItem('cart')) || [];

// Get reference to table body
const cartTable = document.getElementById('cart-items');
let orderTotal = 0;

// Clear table content
cartTable.innerHTML = '';

// Populate cart rows
cart.forEach((item, index) => {
  const row = document.createElement('tr');

  const customizationCharge = (item.customization === 'Patriotic' ? 2 :
                               item.customization !== 'Customize' && item.customization !== '' ? 5 : 0);
  const itemTotal = (item.price + customizationCharge) * item.quantity;
  orderTotal += itemTotal;

  row.innerHTML = `
    <td>${item.name}</td>
    <td>${item.color}</td>
    <td>${item.customization}</td>
    <td>${item.quantity}</td>
    <td>$${itemTotal.toFixed(2)}</td>
    <td><button class="remove-btn" data-index="${index}">🗑️</button></td>
  `;

  cartTable.appendChild(row);
});

// Show order total
document.getElementById('order-total').textContent = `$${orderTotal.toFixed(2)}`;

// Handle removal
document.addEventListener('click', function (e) {
  if (e.target.classList.contains('remove-btn')) {
    const index = e.target.dataset.index;
    cart.splice(index, 1);
    localStorage.setItem('cart', JSON.stringify(cart));
    location.reload(); // Refresh to update view
  }
});
