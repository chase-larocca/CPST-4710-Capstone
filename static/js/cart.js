// cart.js

document.addEventListener('DOMContentLoaded', () => {
  const cart = JSON.parse(localStorage.getItem('cart')) || [];
  const cartTable = document.getElementById('cart-table-body');
  const orderTotalElement = document.getElementById('order-total');
  const selectedAddressElement = document.querySelector('.address-output');
  const addressSection = document.querySelector('.shipping-form');

  let itemSubtotal = 0;
  let customizationFee = 0;
  let totalItems = 0;

  const productImageBaseUrl = '/static/Images/thumbnails/SKU/';

  cart.forEach((item, index) => {
    if (!item.sku || !item.name) {
      console.warn("Skipping item with missing SKU or name:", item);
      return;
    }

    const row = document.createElement('tr');
    const imageUrl = productImageBaseUrl + item.sku + ".png";

    let itemCustomizationFee = 0;
    const militaryCustomizations = [
      'Air Force', 'Marines', 'Army', 'Coast Guard', 'Space Force', 'National Guard', 'Navy'
    ];

    if (item.customization === 'Patriotic') {
      itemCustomizationFee = 2 * item.quantity;
    } else if (militaryCustomizations.includes(item.customization)) {
      itemCustomizationFee = 5 * item.quantity;
    }

    const baseItemTotal = item.price * item.quantity;
    const itemTotal = baseItemTotal + itemCustomizationFee;

    itemSubtotal += baseItemTotal;
    customizationFee += itemCustomizationFee;
    totalItems += item.quantity;

    row.innerHTML = `
      <td class="product-info">
        <img src="${imageUrl}" alt="${item.name}">
        ${item.name}
      </td>
      <td>${item.color}</td>
      <td>${item.customization}</td>
      <td>${item.quantity}</td>
      <td>$${itemTotal.toFixed(2)}</td>
      <td>
        <button class="edit-cart-btn" data-index="${index}">✏️</button>
        <button class="remove-btn" data-index="${index}">🗑️</button>
      </td>
    `;

    cartTable.appendChild(row);
  });

  const grandTotal = itemSubtotal + customizationFee;
  document.getElementById('item-subtotal').innerText = itemSubtotal.toFixed(2);
  document.getElementById('customization-fees').innerText = customizationFee.toFixed(2);
  orderTotalElement.textContent = `$${grandTotal.toFixed(2)}`;

  document.querySelector('.save-address-btn').addEventListener('click', () => {
    const street = document.getElementById('shippingAddress').value.trim();
    const city = document.getElementById('shippingCity').value.trim();
    const state = document.getElementById('shippingState').value.trim();
    const zip = document.getElementById('shippingZip').value.trim();

    if (!street || !city || !state || !zip) {
      alert("Please fill out all shipping fields.");
      return;
    }

    const address = `${street}, ${city}, ${state} ${zip}`;
    selectedAddressElement.textContent = address;
  });

  document.querySelector('.submit-btn').addEventListener('click', () => {
    if (selectedAddressElement.textContent.trim().length < 10) {
      alert('Please enter a valid shipping address.');
      return;
    }

    const orderData = {
      items: cart,
      total: grandTotal,
      NumberOfItems: totalItems,
      shippingAddress: selectedAddressElement.textContent
    };

    fetch('/api/submit-order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(orderData)
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          alert(`Order #${data.orderNumber} submitted successfully!`);
          localStorage.removeItem('cart');
          window.location.href = '/order-status';
        } else {
          alert('Failed to submit order.');
        }
      })
      .catch(error => {
        console.error('Order submission failed:', error);
        alert('An error occurred. Please try again.');
      });
  });

  cartTable.addEventListener('click', (e) => {
    const index = e.target.dataset.index;
    if (e.target.classList.contains('remove-btn')) {
      cart.splice(index, 1);
      localStorage.setItem('cart', JSON.stringify(cart));
      location.reload();
    }
  });
});
