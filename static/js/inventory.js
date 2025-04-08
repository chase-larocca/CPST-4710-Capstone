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
          <td>${item.ItemName}</td>
          <td>${item.ItemDescription || ''}</td>
          <td>${item.Supplier || ''}</td>
          <td>$${parseFloat(item.Price).toFixed(2)}</td>
          <td>${item.QuantityInStock}</td>
          <td>${item.RestockThreshold}</td>
          <td>
            <button class="edit-btn" data-sku="${item.SKU}">Edit</button>
          </td>
        `;
        tableBody.appendChild(row);
      });

      attachEditButtonListeners(data);
    })
    .catch(error => console.error('Error fetching products:', error));
});

  
  function attachEditButtonListeners(inventory) {
    document.querySelectorAll('.edit-btn').forEach(button => {
      button.addEventListener('click', () => {
        const sku = button.dataset.sku;
        const item = inventory.find(i => i.SKU === sku);
        if (!item) return;
  
        const modal = document.getElementById('editModal');
        modal.innerHTML = `
          <div class="modal-content">
            <span class="close-button" id="closeModal">&times;</span>
            <div class="modal-grid">
              <div class="thumbnail-column">
                <img src="https://placehold.co/200x200" alt="Product Thumbnail" class="product-thumbnail">
              </div>
              <div class="fields-column">
                <label>Item Name:</label>
                <input type="text" id="editItemName" value="${item.ItemName || ''}">
  
                <label>Description:</label>
                <textarea id="editItemDesc">${item.ItemDescription || ''}</textarea>
  
                <label>Supplier:</label>
                <input type="text" id="editSupplier" value="${item.Supplier || ''}">
  
                <div class="horizontal-fields">
                  <div class="sku-container">
                    <label>SKU:</label>
                    <input type="text" id="editSKU" value="${item.SKU}" disabled>
                  </div>
                  <div>
                    <label>Price:</label>
                    <input type="number" id="editPrice" class="small-input" value="${item.Price ?? ''}" step="0.01">
                  </div>
                  <div>
                    <label>Quantity:</label>
                    <input type="number" id="editQuantity" class="small-input" value="${item.QuantityInStock ?? ''}">
                  </div>
                  <div>
                    <label>Threshold:</label>
                    <input type="number" id="editRestock" class="small-input" value="${item.RestockThreshold ?? ''}">
                  </div>
                </div>
  
                <button id="update-inventory-btn" type="button">Update</button>
              </div>
            </div>
          </div>
        `;
  
        // Show modal
        modal.style.display = 'flex';
  
        // Add close button handler
        document.getElementById('closeModal').addEventListener('click', () => {
          modal.style.display = 'none';
        });
        
        modal.addEventListener('click', (e) => {
          if (e.target === modal) {
            modal.style.display = 'none';
          }
        });
        
  
        // Add update button handler
        document.getElementById('update-inventory-btn').addEventListener('click', () => {
          const updatedData = {
            SKU: item.SKU,
            ItemName: document.getElementById('editItemName').value,
            ItemDescription: document.getElementById('editItemDesc').value,
            Price: parseFloat(document.getElementById('editPrice').value),
            QuantityInStock: parseInt(document.getElementById('editQuantity').value),
            Supplier: document.getElementById('editSupplier').value,
            RestockThreshold: parseInt(document.getElementById('editRestock').value)
          };
  
          fetch('/api/inventory/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedData)
          })
          .then(response => response.json())
          .then(data => {
            alert('Inventory updated successfully!');
            modal.style.display = 'none';
            location.reload(); 
          })
          .catch(error => {
            console.error('Update failed:', error);
            alert('Failed to update inventory.');
          });
        });
      });
    });
  }
  