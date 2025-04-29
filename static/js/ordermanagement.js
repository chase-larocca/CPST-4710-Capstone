// static/js/ordermanagement.js
document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/admin/orders')
      .then(response => response.json())
      .then(data => {
        const tableBody = document.getElementById('order-management-body');
        tableBody.innerHTML = '';
  
        data.forEach(order => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${order.OrderID}</td>
            <td>${order.FirstName} ${order.LastName}</td>
            <td>${order.ShippingDestination}</td>
            <td>${order.NumberOfItems}</td>
            <td>$${parseFloat(order.TotalPrice).toFixed(2)}</td>
            <td>${order.OrderStatus}</td>
            <td><button class="edit-btn" data-id="${order.OrderID}">Edit</button></td>
          `;
          tableBody.appendChild(row);
        });
  
        attachOrderEditHandlers(data);
      })
      .catch(error => console.error('Failed to load orders:', error));
  });
  
  function attachOrderEditHandlers(orders) {
    document.querySelectorAll('.edit-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.id;
        const order = orders.find(o => o.OrderID == id);
  
        const modal = document.getElementById('editOrderModal');
        modal.innerHTML = `
          <div class="modal-content">
            <span class="close-button" id="closeModal">&times;</span>
            <h2>Edit Order #${order.OrderID}</h2>
            <label>Customer:</label>
            <input type="text" disabled value="${order.FirstName} ${order.LastName}" />
  
            <label>Shipping Address:</label>
            <input type="text" id="edit-shipping" value="${order.ShippingDestination}" />
  
            <label>Number of Items:</label>
            <input type="number" id="edit-qty" value="${order.NumberOfItems}" />
  
            <label>Status:</label>
            <select id="edit-status">
              <option${order.OrderStatus === 'Pending' ? ' selected' : ''}>Pending</option>
              <option${order.OrderStatus === 'Shipped' ? ' selected' : ''}>Shipped</option>
              <option${order.OrderStatus === 'Cancelled' ? ' selected' : ''}>Cancelled</option>
              <option${order.OrderStatus === 'Awaiting Payment' ? ' selected' : ''}>Awaiting Payment</option>
            </select>
  
            <button id="update-order-btn">Save Changes</button>
          </div>
        `;
  
        modal.style.display = 'flex';
  
        document.getElementById('closeModal').onclick = () => modal.style.display = 'none';
  
        document.getElementById('update-order-btn').onclick = () => {
          const updatedOrder = {
            OrderID: order.OrderID,
            ShippingDestination: document.getElementById('edit-shipping').value,
            NumberOfItems: parseInt(document.getElementById('edit-qty').value),
            OrderStatus: document.getElementById('edit-status').value
          };
  
          fetch('/api/admin/orders/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedOrder)
          })
          .then(res => res.json())
          .then(data => {
            alert(data.message || 'Order updated');
            modal.style.display = 'none';
            location.reload();
          })
          .catch(err => {
            console.error('Update failed:', err);
            alert('Failed to update order.');
          });
        };
      });
    });
  }