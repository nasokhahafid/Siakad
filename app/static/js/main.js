// Main JavaScript file for SIAKAD application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize sidebar toggle
    initSidebar();

    // Initialize modal functionality
    initModal();

    // Initialize FAB (Floating Action Button)
    initFAB();

    // Initialize any tooltips or popovers if needed
    initTooltips();
});

// Sidebar functionality
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const menuToggle = document.getElementById('menuToggle');
    const sidebarClose = document.getElementById('sidebarClose');
    const mainContent = document.getElementById('mainContent');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            mainContent.classList.toggle('sidebar-active');
        });
    }

    // Close sidebar with close button
    if (sidebarClose && sidebar) {
        sidebarClose.addEventListener('click', function() {
            sidebar.classList.remove('active');
            mainContent.classList.remove('sidebar-active');
        });
    }

    // Close sidebar when clicking outside on mobile
    if (mainContent) {
        mainContent.addEventListener('click', function() {
            if (window.innerWidth <= 768 && sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
                mainContent.classList.remove('sidebar-active');
            }
        });
    }

    // Initialize collapsible menus
    initCollapsibleMenus();
}

// Collapsible menu functionality
function initCollapsibleMenus() {
    const collapsibleItems = document.querySelectorAll('.sidebar-nav-item.collapsible');

    collapsibleItems.forEach(item => {
        item.addEventListener('click', function() {
            const targetClass = this.getAttribute('data-target');
            const subMenus = document.querySelectorAll(`.sub-menu.${targetClass}`);
            const toggleIcon = this.querySelector('.toggle-icon');

            // Toggle visibility of sub-menus
            subMenus.forEach(subMenu => {
                subMenu.classList.toggle('active');
            });

            // Rotate toggle icon
            if (toggleIcon) {
                toggleIcon.classList.toggle('rotated');
            }
        });
    });
}

// Modal functionality
function initModal() {
    const modal = document.getElementById('modal');

    // Close modal when clicking outside
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
}

// Show modal with custom content
function showModal(title, content, confirmText = 'Confirm', cancelText = 'Cancel', confirmCallback = null, cancelCallback = null) {
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    const modalConfirm = document.getElementById('modalConfirm');
    const modalCancel = document.getElementById('modalCancel');
    const modalFooter = document.getElementById('modalFooter');

    if (modal && modalTitle && modalBody) {
        modalTitle.textContent = title;
        modalBody.innerHTML = content;
        modalConfirm.textContent = confirmText;
        modalCancel.textContent = cancelText;
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';

        // Hide footer if no confirm text
        if (modalFooter && !confirmText) {
            modalFooter.style.display = 'none';
        } else if (modalFooter) {
            modalFooter.style.display = 'flex';
        }

        // Set up event listeners
        modalCancel.onclick = function() {
            if (cancelCallback) {
                cancelCallback();
            } else {
                closeModal();
            }
        };

        modalConfirm.onclick = function() {
            if (confirmCallback) {
                confirmCallback();
            } else {
                closeModal();
            }
        };
    }
}

// Close modal
function closeModal() {
    const modal = document.getElementById('modal');
    const modalFooter = document.getElementById('modalFooter');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
        // Ensure footer is visible for future modals
        if (modalFooter) {
            modalFooter.style.display = 'flex';
        }
    }
}

// FAB functionality
function initFAB() {
    const fab = document.getElementById('fab');
    if (fab) {
        fab.addEventListener('click', function() {
            // Show quick actions menu or perform default action
            showModal('Quick Actions', `
                <div class="fab-actions">
                    <button class="btn btn-primary mb-2" onclick="closeModal(); window.location.href='${window.location.origin}/pengajuan/upload'">
                        <i class="fas fa-upload"></i> Upload Tugas
                    </button>
                    <button class="btn btn-secondary mb-2" onclick="closeModal(); window.location.href='${window.location.origin}/elearning/forum'">
                        <i class="fas fa-comments"></i> Forum Diskusi
                    </button>
                    <button class="btn btn-info" onclick="closeModal(); window.location.href='${window.location.origin}/akademik/profil'">
                        <i class="fas fa-user"></i> Update Profil
                    </button>
                </div>
            `, '', '');
        });
    }
}

// Tooltip functionality
function initTooltips() {
    // Add tooltip functionality if needed
    const tooltipElements = document.querySelectorAll('[data-tooltip]');

    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = e.target.getAttribute('data-tooltip');
    document.body.appendChild(tooltip);

    const rect = e.target.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
}

function hideTooltip() {
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(tooltip => tooltip.remove());
}

// Utility functions
function showAlert(message, type = 'info') {
    // Create and show alert notification
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span>${message}</span>
        <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    // Add to page
    const container = document.querySelector('.main-content') || document.body;
    container.insertBefore(alert, container.firstChild);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alert.parentElement) {
            alert.remove();
        }
    }, 5000);
}

// Confirm dialog
function confirmAction(message, callback) {
    showModal('Konfirmasi', message, 'Ya', 'Tidak',
        // Confirm callback
        function() {
            callback();
            closeModal();
        },
        // Cancel callback
        function() {
            closeModal();
        });
}

// AJAX helper function
function ajaxRequest(url, method = 'GET', data = null, callback = null) {
    const xhr = new XMLHttpRequest();

    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                if (callback) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        callback(response);
                    } catch (e) {
                        callback(xhr.responseText);
                    }
                }
            } else {
                console.error('AJAX Error:', xhr.status, xhr.responseText);
                showAlert('Terjadi kesalahan saat memproses permintaan.', 'error');
            }
        }
    };

    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    if (data) {
        xhr.send(JSON.stringify(data));
    } else {
        xhr.send();
    }
}

// Loading state management
function setLoading(element, loading = true) {
    if (loading) {
        element.setAttribute('disabled', 'true');
        element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    } else {
        element.removeAttribute('disabled');
        // Restore original text (this is a simple implementation)
        element.innerHTML = element.getAttribute('data-original-text') || 'Submit';
    }
}

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validateNIM(nim) {
    return /^\d{9}$/.test(nim);
}

// Download functionality
function initDownloadButtons() {
    const downloadButtons = document.querySelectorAll('.download-btn');

    downloadButtons.forEach(button => {
        button.addEventListener('click', function() {
            const materialId = this.getAttribute('data-material-id');
            if (materialId) {
                downloadMaterial(materialId, this);
            }
        });
    });
}

function downloadMaterial(materialId, button) {
    // Set loading state
    setLoading(button, true);
    button.setAttribute('data-original-text', button.innerHTML);

    // Make AJAX request
    ajaxRequest(`/api/material/${materialId}/download`, 'POST', null, function(response) {
        setLoading(button, false);

        if (response.status === 'success') {
            showAlert(response.message, 'success');

            // In a real app, you would trigger the actual download here
            // For demo purposes, we'll just show success
            if (response.file_url) {
                // Simulate download by opening in new tab (in real app, this would be a secure download URL)
                window.open(response.file_url, '_blank');
            }
        } else {
            showAlert('Gagal mengunduh materi.', 'error');
        }
    });
}

// Initialize download buttons when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // ... existing code ...
    initDownloadButtons();
});

// KHS functionality
function printKHS() {
    // Trigger browser print dialog
    window.print();
}

function downloadKHS() {
    // Show loading state
    const downloadBtn = document.querySelector('button[onclick="downloadKHS()"]');
    if (downloadBtn) {
        downloadBtn.disabled = true;
        downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Mengunduh...';
    }

    // Use fetch to download the PDF
    fetch('/akademik/khs/download', {
        method: 'GET',
        headers: {
            'Accept': 'application/pdf',
        },
        credentials: 'same-origin'  // Include cookies for authentication
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.blob();
    })
    .then(blob => {
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `KHS_${new Date().getFullYear()}.pdf`;
        document.body.appendChild(link);
        link.click();

        // Cleanup
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        // Reset button
        if (downloadBtn) {
            downloadBtn.disabled = false;
            downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download PDF';
        }

        showAlert('KHS berhasil diunduh!', 'success');
    })
    .catch(error => {
        console.error('Download error:', error);

        // Reset button
        if (downloadBtn) {
            downloadBtn.disabled = false;
            downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download PDF';
        }

        showAlert('Gagal mengunduh KHS. Silakan coba lagi.', 'error');
    });
}

// Export functions for global use
window.showModal = showModal;
window.closeModal = closeModal;
window.showAlert = showAlert;
window.confirmAction = confirmAction;
window.ajaxRequest = ajaxRequest;
window.setLoading = setLoading;
window.downloadMaterial = downloadMaterial;
window.printKHS = printKHS;
window.downloadKHS = downloadKHS;
