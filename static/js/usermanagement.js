// static/js/usermanagement.js
document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/admin/users')
      .then(response => response.json())
      .then(data => {
        const tableBody = document.getElementById('user-management-body');
        tableBody.innerHTML = '';
  
        data.forEach(user => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${user.UserID}</td>
            <td>${user.FirstName}</td>
            <td>${user.LastName}</td>
            <td>${user.Email}</td>
            <td>${user.Role}</td>
            <td><button class="edit-btn" data-id="${user.UserID}">Edit</button></td>
          `;
          tableBody.appendChild(row);
        });
  
        attachUserEditHandlers(data);
      })
      .catch(error => console.error('Failed to load users:', error));
  });
  
  function attachUserEditHandlers(users) {
    document.querySelectorAll('.edit-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.id;
        const user = users.find(u => u.UserID == id);
  
        const modal = document.getElementById('editUserModal');
        modal.innerHTML = `
        <div class="modal-content">
            <span class="close-button" id="closeModal">&times;</span>
            <h2>Edit User #${user.UserID}</h2>

            <label>First Name:</label>
            <input type="text" id="edit-firstname" value="${user.FirstName}" />

            <label>Last Name:</label>
            <input type="text" id="edit-lastname" value="${user.LastName}" />

            <label>Email:</label>
            <input type="email" id="edit-email" value="${user.Email}" />

            <label>Role:</label>
            <select id="edit-role">
            <option${user.Role === 'customer' ? ' selected' : ''}>customer</option>
            <option${user.Role === 'inventory_manager' ? ' selected' : ''}>inventory_manager</option>
            <option${user.Role === 'order_manager' ? ' selected' : ''}>order_manager</option>
            <option${user.Role === 'admin' ? ' selected' : ''}>admin</option>
            </select>

            <button id="update-user-btn">Save Changes</button>
        </div>
        `;

  
        modal.style.display = 'flex';
  
        document.getElementById('closeModal').onclick = () => modal.style.display = 'none';
  
        document.getElementById('update-user-btn').onclick = () => {
          const updatedUser = {
            UserID: user.UserID,
            FirstName: document.getElementById('edit-firstname').value,
            LastName: document.getElementById('edit-lastname').value,
            Email: document.getElementById('edit-email').value,
            Role: document.getElementById('edit-role').value
          };
  
          fetch('/api/admin/users/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedUser)
          })
          .then(res => res.json())
          .then(data => {
            alert(data.message || 'User updated');
            modal.style.display = 'none';
            location.reload();
          })
          .catch(err => {
            console.error('Update failed:', err);
            alert('Failed to update user.');
          });
        };
      });
    });
  }
  