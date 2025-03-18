document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/products')
      .then(response => response.json())
      .then(data => {
        const tableBody = document.getElementById('inventory-body');
        if (!tableBody) {
          console.error('inventory-body element not found in DOM.');
          return;
        }
  
        tableBody.innerHTML = '';
  
        data.forEach(item => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${item.SKU}</td>
            <td>${item.ProductName}</td>
            <td>${item.QuantityInStock}</td>
            <td>$${parseFloat(item.Price).toFixed(2)}</td>
          `;
          tableBody.appendChild(row);
        });
      })
      .catch(error => console.error('Error fetching products:', error));
  });
  