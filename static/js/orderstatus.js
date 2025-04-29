fetch('/api/orders')
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    console.log('Fetched orders data:', data);
    const tableBody = document.getElementById('order-status-body');
    tableBody.innerHTML = ''; 

    data.forEach(order => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${order.OrderID}</td>
        <td>${order.ShippingDestination}</td>
        <td>${order.NumberOfItems}</td>
        <td>${order.OrderStatus}</td>
        <td>
          <button class="view-items-btn" data-id="${order.OrderID}">View Items</button>
        </td>
      `;
      tableBody.appendChild(row);
    });
  })
  .catch(error => {
    console.error('Failed to fetch or parse orders:', error);
  });

  document.addEventListener('click', function(e) {
    if (e.target.classList.contains('view-items-btn')) {
      const orderId = e.target.dataset.id;
      fetch(`/api/order/${orderId}/items`)
        .then(response => response.json())
        .then(data => {
          const tableBody = document.getElementById('items-table-body');
          tableBody.innerHTML = ''; // Clear previous
  
          data.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
              <td>${item.ProductName}</td>
              <td>${item.Quantity}</td>
              <td>$${parseFloat(item.Price).toFixed(2)}</td>
            `;
            tableBody.appendChild(row);
          });
  
          document.getElementById('viewItemsModal').style.display = 'flex';
        })
        .catch(error => {
          console.error('Failed to load order items:', error);
          alert('Failed to load items for this order.');
        });
    }
  
    // Close modal handler
    if (e.target.classList.contains('close-view-items')) {
      document.getElementById('viewItemsModal').style.display = 'none';
    }
  });
  
