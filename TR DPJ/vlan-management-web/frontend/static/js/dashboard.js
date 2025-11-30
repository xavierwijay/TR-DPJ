// Dashboard JavaScript

let currentChart = null;

// Load user data on page load
document.addEventListener("DOMContentLoaded", async () => {
  // Load user info
  await loadUserInfo();

  // Setup navigation
  setupNavigation();

  // Setup modals
  setupModals();

  // Load initial data
  await loadOverviewData();

  // Setup event listeners
  setupEventListeners();

  // Load all VLANs
  await loadVlans();

  // Load users
  await loadUsers();

  // Load activities
  await loadActivities();

  // Check device status
  await checkDeviceStatus();
});

// Load user info from server
async function loadUserInfo() {
  try {
    const response = await fetch("/api/users/profile");
    const data = await response.json();

    if (data.success) {
      const user = data.data;
      document.getElementById("userName").textContent = user.name;
      document.getElementById("userNim").textContent = user.nim;

      // Update settings
      document.getElementById("settingName").textContent = user.name;
      document.getElementById("settingNim").textContent = user.nim;
      document.getElementById("settingEmail").textContent = user.email;
      document.getElementById("settingCreatedAt").textContent = new Date(
        user.created_at
      ).toLocaleDateString();
    }
  } catch (error) {
    console.error("Error loading user info:", error);
  }
}

// Setup sidebar navigation
function setupNavigation() {
  const navItems = document.querySelectorAll(".nav-item");

  navItems.forEach((item) => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      const section = item.getAttribute("data-section");

      // Remove active class from all items and sections
      navItems.forEach((ni) => ni.classList.remove("active"));
      document
        .querySelectorAll(".content-section")
        .forEach((cs) => cs.classList.remove("active"));

      // Add active class to clicked item and corresponding section
      item.classList.add("active");
      const contentSection = document.getElementById(section);
      if (contentSection) {
        contentSection.classList.add("active");
        document.getElementById("pageTitle").textContent =
          item.querySelector("span").textContent;
      }
    });
  });

  // Set overview as active by default
  document.querySelector('[data-section="overview"]').classList.add("active");
}

// Setup modals
function setupModals() {
  const modals = document.querySelectorAll(".modal");

  modals.forEach((modal) => {
    // Close modal when clicking close button
    modal.querySelector(".modal-close").addEventListener("click", () => {
      modal.classList.remove("active");
    });

    // Close modal when clicking cancel button
    const closeBtn = modal.querySelector(".modal-close-btn");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        modal.classList.remove("active");
      });
    }

    // Close modal when clicking outside
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        modal.classList.remove("active");
      }
    });
  });
}

// Load overview data
async function loadOverviewData() {
  try {
    const response = await fetch("/api/vlans");
    const data = await response.json();

    if (data.success) {
      const vlans = data.data;

      // Count VLANs by status
      const activeCount = vlans.filter((v) => v.status === "active").length;
      const expiredCount = vlans.filter((v) => v.status === "expired").length;

      // Update card stats
      document.getElementById("totalVlans").textContent = vlans.length;
      document.getElementById("activeVlans").textContent = activeCount;
      document.getElementById("expiredVlans").textContent = expiredCount;

      // Create pie chart
      createVlanChart(vlans);
    }
  } catch (error) {
    console.error("Error loading overview data:", error);
  }
}

// Create VLAN distribution pie chart
function createVlanChart(vlans) {
  const ctx = document.getElementById("vlanChart");
  if (!ctx) return;

  const statusCounts = {
    active: vlans.filter((v) => v.status === "active").length,
    inactive: vlans.filter((v) => v.status === "inactive").length,
    expired: vlans.filter((v) => v.status === "expired").length,
  };

  // Destroy previous chart if exists
  if (currentChart) {
    currentChart.destroy();
  }

  currentChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Active", "Inactive", "Expired"],
      datasets: [
        {
          data: [
            statusCounts.active,
            statusCounts.inactive,
            statusCounts.expired,
          ],
          backgroundColor: ["#10b981", "#6b7280", "#ef4444"],
          borderColor: [
            "rgba(16, 185, 129, 0.2)",
            "rgba(107, 114, 128, 0.2)",
            "rgba(239, 68, 68, 0.2)",
          ],
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            color: "#f1f5f9",
            usePointStyle: true,
            padding: 15,
          },
        },
      },
    },
  });
}

// Load all VLANs
async function loadVlans() {
  try {
    const response = await fetch("/api/vlans");
    const data = await response.json();

    if (data.success) {
      const vlans = data.data;
      const tableBody = document.getElementById("vlansTableBody");

      if (vlans.length === 0) {
        tableBody.innerHTML =
          '<tr><td colspan="8" style="text-align: center; padding: 20px;">No VLANs found</td></tr>';
        return;
      }

      tableBody.innerHTML = vlans
        .map(
          (vlan) => `
                <tr>
                    <td><strong>${vlan.vlan_id}</strong></td>
                    <td>${vlan.vlan_name}</td>
                    <td><span class="status-badge-table ${vlan.status}">${
            vlan.status
          }</span></td>
                    <td>${
                      vlan.user_name
                        ? `${
                            vlan.user_name
                          }<br><small style="color: #94a3b8;">${
                            vlan.user_nim || ""
                          }</small>`
                        : "-"
                    }</td>
                    <td>${vlan.subnet_mask || "-"}</td>
                    <td>${vlan.max_hosts || "-"}</td>
                    <td>${new Date(vlan.created_at).toLocaleDateString()}</td>
                    <td>
                        <div class="action-buttons">
                            <button class="btn btn-small btn-edit" onclick="editVlan('${
                              vlan.id
                            }', '${vlan.vlan_id}', '${vlan.vlan_name}', '${
            vlan.description || ""
          }')">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                            <button class="btn btn-small btn-delete" onclick="deleteVlan('${
                              vlan.id
                            }', ${vlan.vlan_id})">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        </div>
                    </td>
                </tr>
            `
        )
        .join("");
    }
  } catch (error) {
    console.error("Error loading VLANs:", error);
  }
}

// Load users
async function loadUsers() {
  try {
    const response = await fetch("/api/users");
    const data = await response.json();

    if (data.success) {
      const users = data.data;
      const grid = document.getElementById("usersGrid");

      if (users.length === 0) {
        grid.innerHTML =
          '<div style="text-align: center; padding: 20px; grid-column: 1/-1;">No users registered</div>';
        return;
      }

      grid.innerHTML = users
        .map(
          (user) => `
                <div class="user-card">
                    <div class="user-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <h3>${user.name}</h3>
                    <p class="user-nim">${user.nim}</p>
                    <p class="user-email" style="font-size: 12px; color: #cbd5e1;">${user.email}</p>
                    <p class="user-vlans"><i class="fas fa-layer-group"></i> ${user.total_vlans} VLANs</p>
                </div>
            `
        )
        .join("");
    }
  } catch (error) {
    console.error("Error loading users:", error);
  }
}

// Load activities
async function loadActivities() {
  try {
    const response = await fetch("/api/activities?limit=50");
    const data = await response.json();

    if (data.success) {
      const activities = data.data;
      const tableBody = document.getElementById("activitiesTableBody");

      if (activities.length === 0) {
        tableBody.innerHTML =
          '<tr><td colspan="6" style="text-align: center; padding: 20px;">No activities found</td></tr>';
        return;
      }

      tableBody.innerHTML = activities
        .map(
          (activity) => `
                <tr>
                    <td>${new Date(activity.created_at).toLocaleString()}</td>
                    <td>${activity.user_id || "-"}</td>
                    <td><strong>${activity.action}</strong></td>
                    <td>${activity.details || "-"}</td>
                    <td><span class="status-badge-table ${activity.status.toLowerCase()}">${
            activity.status
          }</span></td>
                    <td>${activity.ip_address || "-"}</td>
                </tr>
            `
        )
        .join("");

      // Also update recent activities in overview
      const recentActivities = document.getElementById("recentActivities");
      if (recentActivities) {
        recentActivities.innerHTML = activities
          .slice(0, 5)
          .map(
            (activity) => `
                    <div style="padding: 10px 0; border-bottom: 1px solid var(--border-color);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>${activity.action}</strong>
                                <p style="font-size: 12px; color: var(--text-secondary); margin: 5px 0 0 0;">${
                                  activity.details || "-"
                                }</p>
                            </div>
                            <small style="color: var(--text-secondary);">${new Date(
                              activity.created_at
                            ).toLocaleString()}</small>
                        </div>
                    </div>
                `
          )
          .join("");
      }
    }
  } catch (error) {
    console.error("Error loading activities:", error);
  }
}

// Check device status
async function checkDeviceStatus() {
  try {
    const response = await fetch("/api/device/status");
    const data = await response.json();

    if (data.success && data.data.connected) {
      document.getElementById("deviceStatus").textContent = "Online";
      document.getElementById("deviceStatus").style.color = "#10b981";
      document.getElementById("deviceStatusDetail").textContent = "Online";
      document.getElementById("deviceStatusDetail").className =
        "status-badge active";
    } else {
      document.getElementById("deviceStatus").textContent = "Offline";
      document.getElementById("deviceStatus").style.color = "#ef4444";
      document.getElementById("deviceStatusDetail").textContent = "Offline";
      document.getElementById("deviceStatusDetail").className =
        "status-badge offline";
    }
  } catch (error) {
    console.error("Error checking device status:", error);
  }
}

// Setup event listeners
function setupEventListeners() {
  // Create VLAN button
  document.getElementById("createVlanBtn").addEventListener("click", () => {
    document.getElementById("createVlanForm").reset();
    document.getElementById("createVlanModal").classList.add("active");
  });

  // Create VLAN form submit
  document
    .getElementById("createVlanForm")
    .addEventListener("submit", createVlan);

  // Edit VLAN form submit
  document
    .getElementById("editVlanForm")
    .addEventListener("submit", updateVlan);

  // Auto-delete checkbox
  document.getElementById("autoDelete").addEventListener("change", (e) => {
    document
      .getElementById("expiryOptions")
      .classList.toggle("active", e.target.checked);
  });

  // Subnet mask input - auto-calculate max hosts
  document.getElementById("subnetMask").addEventListener("change", (e) => {
    const mask = e.target.value;
    // Simple calculation for common masks
    const maskMap = {
      "255.255.255.0": "254",
      "255.255.255.128": "126",
      "255.255.255.192": "62",
      "255.255.255.224": "30",
      "255.255.0.0": "65534",
    };

    document.getElementById("maxHosts").value = maskMap[mask] || "N/A";
  });

  // Device buttons
  document
    .getElementById("checkDeviceBtn")
    .addEventListener("click", checkDeviceStatus);
  document
    .getElementById("viewDeviceVlansBtn")
    .addEventListener("click", loadDeviceVlans);

  // Refresh activities button
  document
    .getElementById("refreshActivitiesBtn")
    .addEventListener("click", loadActivities);

  // Save settings button
  document
    .getElementById("saveSettingsBtn")
    .addEventListener("click", saveSettings);

  // Close modals when clicking overlay
  document.querySelectorAll(".modal").forEach((modal) => {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        modal.classList.remove("active");
      }
    });
  });
}

// Create VLAN
async function createVlan(e) {
  e.preventDefault();

  const vlanId = document.getElementById("vlanId").value;
  const vlanName = document.getElementById("vlanName").value;
  const description = document.getElementById("vlanDescription").value;
  const subnetMask = document.getElementById("subnetMask").value;
  const autoDelete = document.getElementById("autoDelete").checked;
  const expiryHours =
    parseInt(document.getElementById("expiryHours").value) || 24;

  try {
    const response = await fetch("/api/vlans", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        vlan_id: parseInt(vlanId),
        vlan_name: vlanName,
        description: description,
        subnet_mask: subnetMask,
        auto_delete: autoDelete,
        expiry_hours: expiryHours,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      showToast("VLAN created successfully", "success");
      document.getElementById("createVlanModal").classList.remove("active");
      await loadVlans();
      await loadOverviewData();
    } else {
      showToast(data.error || "Failed to create VLAN", "error");
    }
  } catch (error) {
    console.error("Error creating VLAN:", error);
    showToast("An error occurred", "error");
  }
}

// Edit VLAN
function editVlan(vlanId, vlanIdNum, vlanName, description) {
  document.getElementById("editVlanId").value = vlanId;
  document.getElementById("editVlanIdField").value = vlanIdNum;
  document.getElementById("editVlanName").value = vlanName;
  document.getElementById("editVlanDescription").value = description;
  document.getElementById("editVlanModal").classList.add("active");
}

// Update VLAN
async function updateVlan(e) {
  e.preventDefault();

  const vlanId = document.getElementById("editVlanId").value;
  const vlanName = document.getElementById("editVlanName").value;
  const description = document.getElementById("editVlanDescription").value;

  try {
    const response = await fetch(`/api/vlans/${vlanId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        vlan_name: vlanName,
        description: description,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      showToast("VLAN updated successfully", "success");
      document.getElementById("editVlanModal").classList.remove("active");
      await loadVlans();
    } else {
      showToast(data.error || "Failed to update VLAN", "error");
    }
  } catch (error) {
    console.error("Error updating VLAN:", error);
    showToast("An error occurred", "error");
  }
}

// Delete VLAN
async function deleteVlan(vlanId, vlanIdNum) {
  if (!confirm(`Are you sure you want to delete VLAN ${vlanIdNum}?`)) {
    return;
  }

  try {
    const response = await fetch(`/api/vlans/${vlanId}`, {
      method: "DELETE",
    });

    const data = await response.json();

    if (response.ok) {
      showToast("VLAN deleted successfully", "success");
      await loadVlans();
      await loadOverviewData();
    } else {
      showToast(data.error || "Failed to delete VLAN", "error");
    }
  } catch (error) {
    console.error("Error deleting VLAN:", error);
    showToast("An error occurred", "error");
  }
}

// Load device VLANs
async function loadDeviceVlans() {
  try {
    const container = document.getElementById("deviceVlansContainer");
    container.innerHTML =
      '<p style="text-align: center;"><i class="fas fa-spinner fa-spin"></i> Loading device VLANs...</p>';

    const response = await fetch("/api/device/vlans");
    const data = await response.json();

    if (response.ok && data.data) {
      const vlans = data.data.device_vlans;

      if (vlans && vlans.length > 0) {
        let html =
          '<table style="width: 100%; border-collapse: collapse;"><thead><tr style="background: rgba(99, 102, 241, 0.1); border-bottom: 1px solid var(--border-color);"><th style="padding: 12px; text-align: left; font-weight: 600; color: var(--primary-color);">VLAN ID</th><th style="padding: 12px; text-align: left; font-weight: 600; color: var(--primary-color);">VLAN Name</th><th style="padding: 12px; text-align: left; font-weight: 600; color: var(--primary-color);">Status</th></tr></thead><tbody>';

        vlans.forEach((vlan) => {
          html += `<tr style="border-bottom: 1px solid var(--border-color);"><td style="padding: 12px;">${
            vlan.vlan_id || "-"
          }</td><td style="padding: 12px;">${
            vlan.vlan_name || "-"
          }</td><td style="padding: 12px;"><span class="status-badge-table active">${
            vlan.status || "active"
          }</span></td></tr>`;
        });

        html += "</tbody></table>";
        container.innerHTML = html;
      } else {
        container.innerHTML =
          '<p style="text-align: center; padding: 20px;">No VLANs found on device</p>';
      }
    } else {
      container.innerHTML =
        '<p style="text-align: center; padding: 20px; color: #ef4444;">Failed to load device VLANs</p>';
    }
  } catch (error) {
    console.error("Error loading device VLANs:", error);
    document.getElementById("deviceVlansContainer").innerHTML =
      '<p style="text-align: center; padding: 20px; color: #ef4444;">Error loading device VLANs</p>';
  }
}

// Save settings
async function saveSettings() {
  const defaultExpiry = document.getElementById("defaultExpiry").value;

  // Store in local storage for now
  localStorage.setItem("defaultExpiry", defaultExpiry);

  showToast("Settings saved successfully", "success");
}

// Show toast notification
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${
          type === "success"
            ? "#10b981"
            : type === "error"
            ? "#ef4444"
            : "#6366f1"
        };
        color: white;
        border-radius: 8px;
        z-index: 3000;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        animation: slideIn 0.3s ease;
    `;
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = "slideOut 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Add CSS animations
const style = document.createElement("style");
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
