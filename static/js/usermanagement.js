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
            <td>
              <div class="user-actions">
                <button class="edit-btn" data-id="${user.UserID}">Edit</button>
                <button class="delete-btn" data-id="${user.UserID}">Delete</button>
              </div>
            </td>


          `;
          tableBody.appendChild(row);
        });
  
        attachUserEditHandlers(data);
      })
      .catch(error => console.error('Failed to load users:', error));

      const addUserBtn = document.getElementById('addUserBtn');
      const addUserModal = document.getElementById('addUserModal');
      const closeAddUserBtn = document.querySelector('.close-add-user');
    
      addUserBtn.addEventListener('click', () => {
        addUserModal.style.display = 'flex';
      });
    
      closeAddUserBtn.addEventListener('click', () => {
        addUserModal.style.display = 'none';
      });
    
      window.addEventListener('click', (e) => {
        if (e.target === addUserModal) {
          addUserModal.style.display = 'none';
        }
      });

      document.addEventListener('click', (e) => {
        if (e.target.classList.contains('delete-btn')) {
          const userId = e.target.dataset.id;
          const confirmed = confirm("Are you sure you want to delete this user?");
      
          if (confirmed) {
            fetch(`/api/admin/users/${userId}`, {
              method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
              if (data.success) {
                showToast("User deleted successfully.");
                setTimeout(() => location.reload(), 2000); // Delay to allow toast to show

              } else {
                showToast("Failed to delete user.");

              }
            })
            .catch(error => {
              console.error('Error deleting user:', error);
              alert("An error occurred. Please try again.");
            });
          }
        }
      });
      
      document.getElementById('submitNewUserBtn').addEventListener('click', () => {
        const newUserData = {
          FirstName: document.getElementById('new-firstname').value.trim(),
          LastName: document.getElementById('new-lastname').value.trim(),
          Email: document.getElementById('new-email').value.trim(),
          Username: document.getElementById('new-username').value.trim(),
          Password: document.getElementById('new-password').value.trim(),
          ConfirmPassword: document.getElementById('confirm-password').value.trim(),
          Role: document.getElementById('new-role').value
        };
      
        if (!newUserData.FirstName || !newUserData.LastName || !newUserData.Email ||
            !newUserData.Username || !newUserData.Password || !newUserData.ConfirmPassword) {
          alert("Please fill out all fields.");
          return;
        }
      
        if (newUserData.Password !== newUserData.ConfirmPassword) {
          alert("Passwords do not match!");
          return;
        }
      
        fetch('/api/admin/users/add', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(newUserData)
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            alert("User added successfully!");
            document.getElementById('addUserModal').style.display = 'none';
            location.reload();
          } else {
            alert("Failed to add user: " + (data.error || ""));
          }
        })
        .catch(error => {
          console.error('Failed to add user:', error);
          alert("An error occurred. Please try again.");
        });
      });
      
  });

  function showToast(message, duration = 3000, type = 'success') {
    const toast = document.getElementById('toast');
    if (!toast) return;
  
    toast.textContent = message;
    toast.style.backgroundColor = type === 'error' ? '#d9534f' : 'var(--primary-green)';
    toast.classList.remove('hidden');
    toast.classList.add('show');
  
    setTimeout(() => {
      toast.classList.remove('show');
      toast.classList.add('hidden');
    }, duration);
  }
  
  
  
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
            <option${user.Role === 'Customer' ? ' selected' : ''}>Customer</option>
            <option${user.Role === 'Employee' ? ' selected' : ''}>Employee</option>
            <option${user.Role === 'Admin' ? ' selected' : ''}>Admin</option>
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
            if (data.success) {
              showToast("User updated successfully.");
              modal.style.display = 'none';
              setTimeout(() => location.reload(), 1000); // Let toast show
            } else {
              showToast("Failed to update user.", 3000, 'error');
            }
          })
          .catch(err => {
            console.error('Update failed:', err);
            showToast("An error occurred while updating.", 3000, 'error');
          });
          
        };
      });
    });
  }
  