fetch('/api/orders')
  .then(response => response.json())
  .then(data => {
    const tableBody = document.getElementById('order-table-body');
    tableBody.innerHTML = ''; 

    data.forEach(order => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${order.OrderNumber}</td>
        <td>${order.ShippingDestination}</td>
        <td>${order.NumberOfItems}</td>
        <td>${order.OrderStatus}</td>
      `;
      tableBody.appendChild(row);
    });
  })
  .catch(error => console.error('Error loading order status:', error));
