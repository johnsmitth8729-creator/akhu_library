document.addEventListener("DOMContentLoaded", () => {
    const mobileBtn = document.getElementById("mobileMenuBtn");
    const mobileMenu = document.getElementById("mobileMenu");

    const notificationBtn = document.getElementById("notificationBtn");
    const notificationDropdown = document.getElementById("notificationDropdown");

    const languageBtn = document.getElementById("languageBtn");
    const languageDropdown = document.getElementById("languageDropdown");

    if (mobileBtn && mobileMenu) {
        mobileBtn.addEventListener("click", (event) => {
            event.stopPropagation();

            mobileMenu.classList.toggle("active");

            if (notificationDropdown) {
                notificationDropdown.classList.remove("show");
            }

            if (languageDropdown) {
                languageDropdown.classList.remove("show");
            }
        });
    }

    if (notificationBtn && notificationDropdown) {
        notificationBtn.addEventListener("click", (event) => {
            event.stopPropagation();

            notificationDropdown.classList.toggle("show");

            if (mobileMenu) {
                mobileMenu.classList.remove("active");
            }

            if (languageDropdown) {
                languageDropdown.classList.remove("show");
            }
        });

        notificationDropdown.addEventListener("click", (event) => {
            event.stopPropagation();
        });
    }

    if (languageBtn && languageDropdown) {
        languageBtn.addEventListener("click", (event) => {
            event.stopPropagation();

            languageDropdown.classList.toggle("show");

            if (mobileMenu) {
                mobileMenu.classList.remove("active");
            }

            if (notificationDropdown) {
                notificationDropdown.classList.remove("show");
            }
        });

        languageDropdown.addEventListener("click", (event) => {
            event.stopPropagation();
        });
    }

    document.addEventListener("click", () => {
        if (mobileMenu) {
            mobileMenu.classList.remove("active");
        }

        if (notificationDropdown) {
            notificationDropdown.classList.remove("show");
        }

        if (languageDropdown) {
            languageDropdown.classList.remove("show");
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            if (mobileMenu) {
                mobileMenu.classList.remove("active");
            }

            if (notificationDropdown) {
                notificationDropdown.classList.remove("show");
            }

            if (languageDropdown) {
                languageDropdown.classList.remove("show");
            }
        }
    });

    document.querySelectorAll(".flash").forEach((flash) => {
        setTimeout(() => {
            flash.style.opacity = "0";
            flash.style.transform = "translateY(-10px)";

            setTimeout(() => {
                flash.remove();
            }, 350);
        }, 5000);
    });

    const filterForm = document.querySelector(".filters");

    if (filterForm) {
        const input = filterForm.querySelector('input[name="q"]');

        if (input) {
            let timer;

            input.addEventListener("input", () => {
                clearTimeout(timer);

                timer = setTimeout(() => {
                    filterForm.submit();
                }, 600);
            });
        }
    }

    const escapeHtml = (value) => String(value || "").replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    }[char]));

    const renderNotifications = (payload) => {
        if (!notificationBtn || !notificationDropdown || !payload || !payload.success) {
            return;
        }

        const unreadCount = Number(payload.unread_count || 0);
        let badge = notificationBtn.querySelector(".notification-badge");

        if (unreadCount > 0) {
            if (!badge) {
                badge = document.createElement("span");
                badge.className = "notification-badge";
                notificationBtn.appendChild(badge);
            }

            badge.textContent = unreadCount > 99 ? "99+" : unreadCount;
        } else if (badge) {
            badge.remove();
        }

        const notifications = Array.isArray(payload.notifications)
            ? payload.notifications
            : [];

        const header = notificationDropdown.querySelector(".notification-header");
        const footerUrl = "/user/notifications";
        const bodyHtml = notifications.length
            ? `
                <div class="notification-list">
                    ${notifications.map((notification) => `
                        <div class="notification-item">
                            <span class="notification-dot"></span>
                            <div class="notification-content">
                                <p>${escapeHtml(notification.message)}</p>
                                <span>${escapeHtml(notification.created_at)}</span>
                            </div>
                        </div>
                    `).join("")}
                </div>
                <div class="notification-footer">
                    <a href="${footerUrl}">View all notifications</a>
                </div>
            `
            : `
                <div class="empty-notifications">
                    <i class="fas fa-bell-slash"></i>
                    <span>No notifications yet.</span>
                </div>
            `;

        notificationDropdown.innerHTML = `${header ? header.outerHTML : ""}${bodyHtml}`;
    };

    const refreshNotifications = async () => {
        if (!notificationBtn || !notificationDropdown || document.hidden) {
            return;
        }

        try {
            const response = await fetch("/api/notifications/latest", {
                headers: {
                    "Accept": "application/json"
                },
                credentials: "same-origin"
            });

            if (response.ok) {
                renderNotifications(await response.json());
            }
        } catch (error) {
            // Silent retry on the next interval keeps the UI calm if the server is restarting.
        }
    };

    if (notificationBtn && notificationDropdown) {
        refreshNotifications();
        setInterval(refreshNotifications, 10000);
    }

    const autoRefreshPaths = [
        "/admin/dashboard",
        "/admin/statistics",
        "/admin/activity",
        "/librarian/dashboard",
        "/librarian/requests",
        "/librarian/borrowings"
    ];

    const canAutoReload = () => {
        const activeElement = document.activeElement;
        const isEditing = activeElement && (
            activeElement.matches("input, textarea, select") ||
            activeElement.isContentEditable
        );

        return !document.hidden &&
            !isEditing &&
            !document.querySelector(".modal.show, .notification-dropdown.show, .language-dropdown.show");
    };

    if (autoRefreshPaths.includes(window.location.pathname)) {
        setInterval(() => {
            if (canAutoReload()) {
                window.location.reload();
            }
        }, 45000);
    }

    // Dynamic active state indicators for navbar
    const currentPath = window.location.pathname;
    document.querySelectorAll(".nav-links a").forEach((link) => {
        const href = link.getAttribute("href");
        if (href === currentPath || (currentPath.startsWith(href) && href !== "/")) {
            link.classList.add("active");
        }
    });
});
