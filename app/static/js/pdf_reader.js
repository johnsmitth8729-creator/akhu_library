document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("pdf-render");
    const container = document.getElementById("pdf-container");
    const loader = document.getElementById("pdf-loader");
    const pageNumEl = document.getElementById("page-num");
    const pageCountEl = document.getElementById("page-count");
    const mobilePageNumEl = document.getElementById("mobile-page-num");
    const mobilePageCountEl = document.getElementById("mobile-page-count");
    const progressBar = document.getElementById("readingProgressBar");

    if (!canvas || !container) {
        return;
    }

    const url = canvas.dataset.url;
    const progressUrl = canvas.dataset.progressUrl;
    const bookmarkUrl = canvas.dataset.bookmarkUrl;
    const csrfToken = canvas.dataset.csrf;
    const isProtected = canvas.dataset.protected === "true";

    let pdfDoc = null;
    let pageNum = parseInt(canvas.dataset.initialPage || "1", 10);
    let scale = 1.35;
    let rotation = 0;
    let pendingRender = null;
    let saveTimer = null;
    let isMobile = () => window.innerWidth <= 767;

    const bookmarkKey = "akhu-bookmarks-" + window.location.pathname;

    /* ─────────────────────────────────────────
       Loader helpers
     ───────────────────────────────────────── */
    function setLoaderVisible(visible) {
        if (loader) {
            loader.style.display = visible ? "flex" : "none";
        }
    }

    function showFallback(message) {
        setLoaderVisible(false);
        const retryHint = isProtected
            ? "<p class=\"small\">Please return to the book page and open Read Online again.</p>"
            : "";
        container.innerHTML = `
            <div class="pdf-fallback-message">
                <h3>PDF preview is unavailable</h3>
                <p>${message}</p>
                ${retryHint}
            </div>
        `;
    }

    /* ─────────────────────────────────────────
       Protection layer
     ───────────────────────────────────────── */
    function blockProtectedShortcuts(event) {
        if (!isProtected) return;
        const key = event.key.toLowerCase();
        const ctrl = event.ctrlKey || event.metaKey;
        if (ctrl && (key === "p" || key === "s")) {
            event.preventDefault();
        }
        if (event.ctrlKey && event.shiftKey && key === "s") {
            event.preventDefault();
        }
    }

    function enableProtectionLayer() {
        if (!isProtected) return;
        document.addEventListener("keydown", blockProtectedShortcuts);
        document.addEventListener("contextmenu", (event) => {
            if (container.contains(event.target)) {
                event.preventDefault();
            }
        });
        window.addEventListener("beforeprint", (event) => {
            event.preventDefault();
        });
    }

    /* ─────────────────────────────────────────
       Progress bar & save
     ───────────────────────────────────────── */
    function updateProgressBar() {
        if (!pdfDoc || !progressBar) return;
        const percent = Math.min(100, Math.max(0, (pageNum / pdfDoc.numPages) * 100));
        progressBar.style.width = `${percent}%`;
    }

    function updatePageIndicators(num) {
        if (pageNumEl) pageNumEl.textContent = num;
        if (mobilePageNumEl) mobilePageNumEl.textContent = num;
        updateScrubberValue(num);
    }

    function updatePageCountIndicators(total) {
        if (pageCountEl) pageCountEl.textContent = total;
        if (mobilePageCountEl) mobilePageCountEl.textContent = total;
        initScrubber(total);
    }

    function saveProgress() {
        if (!progressUrl) return;
        clearTimeout(saveTimer);
        saveTimer = setTimeout(() => {
            fetch(progressUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({ page: pageNum })
            }).catch(() => {});
        }, 350);
    }

    /* ─────────────────────────────────────────
       Fit-width calculation
     ───────────────────────────────────────── */
    function calcFitWidthScale(page) {
        const padding = isMobile() ? 12 : 40; 
        let availableWidth = container.clientWidth - padding;
        if (availableWidth <= 0) {
            availableWidth = window.innerWidth - (isMobile() ? 24 : 80);
        }
        const viewport = page.getViewport({ scale: 1, rotation });
        return availableWidth / viewport.width;
    }

    function fitWidth() {
        if (!pdfDoc) return;
        pdfDoc.getPage(pageNum).then((page) => {
            scale = calcFitWidthScale(page);
            scale = Math.max(0.5, Math.min(4, scale));
            renderPage(pageNum);
        });
    }

    /* ─────────────────────────────────────────
       Render page
     ───────────────────────────────────────── */
    function renderPage(num) {
        if (!pdfDoc) return;

        if (pendingRender) {
            pendingRender.cancel();
            pendingRender = null;
        }

        pdfDoc.getPage(num).then((page) => {
            const viewport = page.getViewport({ scale, rotation });
            const ctx = canvas.getContext("2d");

            canvas.height = viewport.height;
            canvas.width = viewport.width;

            pendingRender = page.render({ canvasContext: ctx, viewport });

            pendingRender.promise.finally(() => {
                pendingRender = null;
            }).catch(() => {});

            updatePageIndicators(num);
            updateProgressBar();
            saveProgress();
        });
    }

    function goToPage(nextPage) {
        if (!pdfDoc) return;
        pageNum = Math.min(pdfDoc.numPages, Math.max(1, nextPage));
        renderPage(pageNum);
    }

    /* ─────────────────────────────────────────
       Rotation controls
     ───────────────────────────────────────── */
    function rotateLeft() {
        rotation = (rotation - 90 + 360) % 360;
        fitWidth();
    }

    function rotateRight() {
        rotation = (rotation + 90) % 360;
        fitWidth();
    }

    /* ─────────────────────────────────────────
       Theme Engine
     ───────────────────────────────────────── */
    function initTheme() {
        const savedTheme = localStorage.getItem("akhu-reader-theme") || "light";
        setTheme(savedTheme);
    }

    function setTheme(theme) {
        document.body.setAttribute("data-reader-theme", theme);
        localStorage.setItem("akhu-reader-theme", theme);
        
        // Sync active states of the buttons
        document.querySelectorAll(".theme-opt-btn").forEach(btn => {
            if (btn.dataset.theme === theme) {
                btn.classList.add("active");
            } else {
                btn.classList.remove("active");
            }
        });
    }

    /* ─────────────────────────────────────────
       Table of Contents (Outline)
     ───────────────────────────────────────── */
    function loadOutline() {
        if (!pdfDoc) return;
        pdfDoc.getOutline().then((outline) => {
            renderOutline(outline);
        }).catch(() => {
            renderOutline(null);
        });
    }

    function renderOutline(outline) {
        const tocContainer = document.getElementById("toc-list");
        const mobileTocContainer = document.getElementById("mobile-toc-list");
        
        function buildTree(container, outlineItems) {
            if (!container) return;
            
            if (!outlineItems || outlineItems.length === 0) {
                container.innerHTML = `
                    <div class="toc-placeholder">
                        <i class="fas fa-folder-open"></i>
                        <p>No table of contents available.</p>
                    </div>
                `;
                return;
            }

            container.innerHTML = "";
            const list = document.createElement("div");
            list.className = "toc-list-container";
            
            function buildItems(items, depth = 1) {
                items.forEach((item) => {
                    const link = document.createElement("a");
                    link.className = `toc-item level-${Math.min(depth, 4)}`;
                    link.textContent = item.title;
                    link.href = "#";
                    link.addEventListener("click", (e) => {
                        e.preventDefault();
                        if (item.dest) {
                            resolveOutlineDest(item.dest);
                            closeMobileSheet();
                        }
                    });
                    list.appendChild(link);
                    
                    if (item.items && item.items.length > 0) {
                        buildItems(item.items, depth + 1);
                    }
                });
            }
            
            buildItems(outlineItems);
            container.appendChild(list);
        }

        buildTree(tocContainer, outline);
        buildTree(mobileTocContainer, outline);
    }

    function resolveOutlineDest(dest) {
        if (typeof dest === "string") {
            pdfDoc.getDestination(dest).then((resolved) => {
                if (resolved && resolved[0]) {
                    resolveRef(resolved[0]);
                }
            });
        } else if (Array.isArray(dest)) {
            resolveRef(dest[0]);
        }
    }

    function resolveRef(ref) {
        if (typeof ref === "object" && ref !== null) {
            pdfDoc.getPageIndex(ref).then((idx) => {
                goToPage(idx + 1);
            }).catch(() => {});
        } else if (typeof ref === "number") {
            goToPage(ref + 1);
        }
    }

    /* ─────────────────────────────────────────
       Local Bookmarks
     ───────────────────────────────────────── */
    function getLocalBookmarks() {
        try {
            return JSON.parse(localStorage.getItem(bookmarkKey)) || [];
        } catch(e) {
            return [];
        }
    }

    function toggleLocalBookmark(page) {
        let bookmarks = getLocalBookmarks();
        if (bookmarks.includes(page)) {
            bookmarks = bookmarks.filter(p => p !== page);
        } else {
            bookmarks.push(page);
            bookmarks.sort((a, b) => a - b);
        }
        localStorage.setItem(bookmarkKey, JSON.stringify(bookmarks));
        renderLocalBookmarks();
    }

    function deleteLocalBookmark(page) {
        let bookmarks = getLocalBookmarks();
        bookmarks = bookmarks.filter(p => p !== page);
        localStorage.setItem(bookmarkKey, JSON.stringify(bookmarks));
        renderLocalBookmarks();
    }

    function renderLocalBookmarks() {
        const listContainer = document.getElementById("bookmarks-list");
        const mobileListContainer = document.getElementById("mobile-bookmarks-list");
        
        const buildBookmarksHtml = (bookmarks) => {
            if (bookmarks.length === 0) {
                return `
                    <div class="bookmarks-placeholder">
                        <i class="fas fa-bookmark"></i>
                        <p>No saved bookmarks.</p>
                        <span class="small-text">Click the bookmark button to save pages here.</span>
                    </div>
                `;
            }
            
            let html = '<div class="bookmarks-list-container">';
            bookmarks.forEach((page) => {
                html += `
                    <div class="bookmark-item">
                        <a href="#" class="bookmark-link" data-page="${page}">
                            <i class="fas fa-bookmark text-primary"></i> Page ${page}
                        </a>
                        <button class="bookmark-delete-btn" data-page="${page}" title="Delete">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                `;
            });
            html += '</div>';
            return html;
        };

        const bookmarks = getLocalBookmarks();
        const html = buildBookmarksHtml(bookmarks);
        
        if (listContainer) {
            listContainer.innerHTML = html;
            listContainer.querySelectorAll(".bookmark-link").forEach(link => {
                link.addEventListener("click", (e) => {
                    e.preventDefault();
                    goToPage(parseInt(link.dataset.page, 10));
                });
            });
            listContainer.querySelectorAll(".bookmark-delete-btn").forEach(btn => {
                btn.addEventListener("click", (e) => {
                    e.stopPropagation();
                    deleteLocalBookmark(parseInt(btn.dataset.page, 10));
                });
            });
        }
        
        if (mobileListContainer) {
            mobileListContainer.innerHTML = html;
            mobileListContainer.querySelectorAll(".bookmark-link").forEach(link => {
                link.addEventListener("click", (e) => {
                    e.preventDefault();
                    goToPage(parseInt(link.dataset.page, 10));
                    closeMobileSheet();
                });
            });
            mobileListContainer.querySelectorAll(".bookmark-delete-btn").forEach(btn => {
                btn.addEventListener("click", (e) => {
                    e.stopPropagation();
                    deleteLocalBookmark(parseInt(btn.dataset.page, 10));
                });
            });
        }
    }

    /* ─────────────────────────────────────────
       Range Scrubber Slider
     ───────────────────────────────────────── */
    function initScrubber(totalPages) {
        const scrubber = document.getElementById("page-scrubber");
        const mScrubber = document.getElementById("mobile-scrubber");
        const pageInput = document.getElementById("page-input");
        
        [scrubber, mScrubber].forEach(sc => {
            if (sc) {
                sc.min = 1;
                sc.max = totalPages;
                sc.value = pageNum;
            }
        });
        
        if (pageInput) {
            pageInput.max = totalPages;
        }
    }

    function updateScrubberValue(num) {
        const scrubber = document.getElementById("page-scrubber");
        const mScrubber = document.getElementById("mobile-scrubber");
        const pageInput = document.getElementById("page-input");
        
        [scrubber, mScrubber].forEach(sc => {
            if (sc) sc.value = num;
        });
        
        if (pageInput) pageInput.value = num;
    }

    /* ─────────────────────────────────────────
       Fullscreen & Auto-Hide
     ───────────────────────────────────────── */
    function enterFullscreen() {
        document.body.classList.add("reader-fullscreen");
        const el = document.documentElement;
        if (el.requestFullscreen) {
            el.requestFullscreen().catch(() => {});
        } else if (el.webkitRequestFullscreen) {
            el.webkitRequestFullscreen();
        }
        syncFullscreenButtons(true);
        requestAnimationFrame(() => {
            setTimeout(() => fitWidth(), 80);
        });
    }

    function exitFullscreen() {
        document.body.classList.remove("reader-fullscreen");
        if (document.exitFullscreen) {
            document.exitFullscreen().catch(() => {});
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        }
        syncFullscreenButtons(false);
        requestAnimationFrame(() => {
            setTimeout(() => fitWidth(), 120);
        });
    }

    function isFullscreen() {
        return document.body.classList.contains("reader-fullscreen");
    }

    function toggleFullscreen() {
        if (isFullscreen()) {
            exitFullscreen();
        } else {
            enterFullscreen();
        }
    }

    function syncFullscreenButtons(active) {
        const compressIcon = '<i class="fas fa-compress"></i>';
        const expandIcon   = '<i class="fas fa-expand"></i>';
        const icon  = active ? compressIcon : expandIcon;
        const label = active ? "Exit Fullscreen" : "Fullscreen";

        const desktopBtn = document.getElementById("fullscreen-btn");
        if (desktopBtn) {
            desktopBtn.innerHTML = `${icon} <span class="reader-btn-label">${label}</span>`;
            desktopBtn.setAttribute("aria-label", label);
        }

        const mobileBtn = document.getElementById("mobile-fullscreen");
        if (mobileBtn) {
            mobileBtn.innerHTML = icon;
            mobileBtn.setAttribute("aria-label", label);
        }

        const sheetBtn = document.getElementById("sheet-fullscreen-btn");
        if (sheetBtn) {
            sheetBtn.innerHTML = `${icon} ${label}`;
        }
    }

    document.addEventListener("fullscreenchange", () => {
        const nativeActive = !!document.fullscreenElement;
        if (!nativeActive && isFullscreen()) {
            document.body.classList.remove("reader-fullscreen");
            syncFullscreenButtons(false);
        }
    });

    // Immersive Auto-hide controls in fullscreen
    let idleTimer;
    function resetIdleTimer() {
        // Remove hide classes from toolbars
        document.querySelectorAll(".pdf-toolbar, #readerMobileToolbar, #readerTopbar").forEach(el => {
            el.classList.remove("fullscreen-controls-hide");
        });
        
        clearTimeout(idleTimer);
        
        if (!isFullscreen()) return;

        idleTimer = setTimeout(() => {
            if (isFullscreen()) {
                document.querySelectorAll(".pdf-toolbar, #readerMobileToolbar, #readerTopbar").forEach(el => {
                    el.classList.add("fullscreen-controls-hide");
                });
            }
        }, 3000);
    }

    ["mousemove", "mousedown", "touchstart", "touchmove", "keydown"].forEach(evt => {
        window.addEventListener(evt, resetIdleTimer, { passive: true });
    });

    /* ─────────────────────────────────────────
       Swipe gestures (mobile)
     ───────────────────────────────────────── */
    let touchStartX = 0;
    let touchStartY = 0;

    container.addEventListener("touchstart", (e) => {
        touchStartX = e.changedTouches[0].clientX;
        touchStartY = e.changedTouches[0].clientY;
    }, { passive: true });

    container.addEventListener("touchend", (e) => {
        const dx = e.changedTouches[0].clientX - touchStartX;
        const dy = e.changedTouches[0].clientY - touchStartY;

        if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) {
            if (dx < 0) {
                goToPage(pageNum + 1); 
            } else {
                goToPage(pageNum - 1); 
            }
        }
    }, { passive: true });

    /* ─────────────────────────────────────────
       Sidebar Navigation
     ───────────────────────────────────────── */
    const sidebarToggleBtn = document.getElementById("sidebar-toggle-btn");
    const sidebarCloseBtn = document.getElementById("sidebarCloseBtn");
    const readerSidebar = document.getElementById("readerSidebar");

    function toggleSidebar() {
        if (readerSidebar) {
            readerSidebar.classList.toggle("collapsed");
            setTimeout(() => fitWidth(), 300);
        }
    }

    if (sidebarToggleBtn) sidebarToggleBtn.addEventListener("click", toggleSidebar);
    if (sidebarCloseBtn) sidebarCloseBtn.addEventListener("click", toggleSidebar);

    // Sidebar tab switching
    document.querySelectorAll(".sidebar-tabs .tab-btn").forEach(btn => {
        btn.addEventListener("click", function() {
            document.querySelectorAll(".sidebar-tabs .tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".sidebar-tab-content").forEach(b => b.classList.remove("active"));

            this.classList.add("active");
            const targetId = "tab-content-" + this.dataset.tab;
            const targetContent = document.getElementById(targetId);
            if (targetContent) targetContent.classList.add("active");
        });
    });

    /* ─────────────────────────────────────────
       Mobile Bottom Sheet
     ───────────────────────────────────────── */
    const mobileMenuBtn = document.getElementById("mobile-menu-btn");
    const mobileBottomSheet = document.getElementById("mobileBottomSheet");
    const sheetCloseBtn = document.getElementById("sheetCloseBtn");
    const sheetBackdrop = document.getElementById("sheetBackdrop");

    function openMobileSheet() {
        if (mobileBottomSheet) {
            mobileBottomSheet.classList.add("active");
            mobileBottomSheet.setAttribute("aria-hidden", "false");
        }
    }

    function closeMobileSheet() {
        if (mobileBottomSheet) {
            mobileBottomSheet.classList.remove("active");
            mobileBottomSheet.setAttribute("aria-hidden", "true");
        }
    }

    if (mobileMenuBtn) mobileMenuBtn.addEventListener("click", openMobileSheet);
    if (sheetCloseBtn) sheetCloseBtn.addEventListener("click", closeMobileSheet);
    if (sheetBackdrop) sheetBackdrop.addEventListener("click", closeMobileSheet);

    // Sheet tab switching
    document.querySelectorAll(".sheet-tabs .sheet-tab-btn").forEach(btn => {
        btn.addEventListener("click", function() {
            document.querySelectorAll(".sheet-tabs .sheet-tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".sheet-tab-body").forEach(b => b.classList.remove("active"));

            this.classList.add("active");
            const targetId = "sheet-tab-" + this.dataset.sheetTab;
            const targetBody = document.getElementById(targetId);
            if (targetBody) targetBody.classList.add("active");
        });
    });

    /* ─────────────────────────────────────────
       Settings Menu Dropdown (Desktop)
     ───────────────────────────────────────── */
    const themeMenuBtn = document.getElementById("theme-menu-btn");
    const themeDropdownMenu = document.getElementById("themeDropdownMenu");

    if (themeMenuBtn && themeDropdownMenu) {
        themeMenuBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            const active = themeDropdownMenu.classList.toggle("active");
            themeMenuBtn.setAttribute("aria-expanded", active);
        });

        document.addEventListener("click", (e) => {
            if (!themeDropdownMenu.contains(e.target) && e.target !== themeMenuBtn) {
                themeDropdownMenu.classList.remove("active");
                themeMenuBtn.setAttribute("aria-expanded", "false");
            }
        });
    }

    /* ─────────────────────────────────────────
       Bind all controls
     ───────────────────────────────────────── */
    function bindControls() {
        // ── Desktop Toolbar controls ──
        const prevBtn = document.getElementById("prev-page");
        const nextBtn = document.getElementById("next-page");
        const zoomInBtn = document.getElementById("zoom-in");
        const zoomOutBtn = document.getElementById("zoom-out");
        const fitWidthBtn = document.getElementById("fit-width-btn");
        const fullscreenBtn = document.getElementById("fullscreen-btn");
        const bookmarkBtn = document.getElementById("bookmark-page");
        const pageInput = document.getElementById("page-input");
        const scrubber = document.getElementById("page-scrubber");

        // ── Settings Dropdown controls (Desktop) ──
        const rotateLeftTop = document.getElementById("rotate-left-top");
        const rotateRightTop = document.getElementById("rotate-right-top");

        // ── Mobile Bottom Sheet controls ──
        const mPrev = document.getElementById("mobile-prev");
        const mNext = document.getElementById("mobile-next");
        const mZoomIn = document.getElementById("mobile-zoom-in");
        const mZoomOut = document.getElementById("mobile-zoom-out");
        const mFitWidth = document.getElementById("mobile-fit-width");
        const mRotateLeft = document.getElementById("mobile-rotate-left");
        const mRotateRight = document.getElementById("mobile-rotate-right");
        const mScrubber = document.getElementById("mobile-scrubber");
        const mBookmarkBtn = document.getElementById("mobile-bookmark-btn");

        // Prev / Next
        [prevBtn, mPrev].forEach(btn => btn && btn.addEventListener("click", () => goToPage(pageNum - 1)));
        [nextBtn, mNext].forEach(btn => btn && btn.addEventListener("click", () => goToPage(pageNum + 1)));

        // Zoom
        [zoomInBtn, mZoomIn].forEach(btn => btn && btn.addEventListener("click", () => {
            scale = Math.min(4, scale + 0.2);
            renderPage(pageNum);
        }));

        [zoomOutBtn, mZoomOut].forEach(btn => btn && btn.addEventListener("click", () => {
            scale = Math.max(0.4, scale - 0.2);
            renderPage(pageNum);
        }));

        // Fit Width
        [fitWidthBtn, mFitWidth].forEach(btn => btn && btn.addEventListener("click", () => fitWidth()));

        // Rotation
        [rotateLeftTop, mRotateLeft].forEach(btn => btn && btn.addEventListener("click", rotateLeft));
        [rotateRightTop, mRotateRight].forEach(btn => btn && btn.addEventListener("click", rotateRight));

        // Fullscreen
        const mFullscreen = document.getElementById("mobile-fullscreen");
        const sheetFullscreen = document.getElementById("sheet-fullscreen-btn");

        [fullscreenBtn, mFullscreen, sheetFullscreen].forEach(btn => {
            if (btn) {
                btn.addEventListener("click", () => {
                    toggleFullscreen();
                    closeMobileSheet();
                });
            }
        });

        // Bookmark (Server Sync + Local Storage Bookmark)
        const performBookmarkAction = () => {
            // Toggle local bookmark first
            toggleLocalBookmark(pageNum);

            // Sync with Server DB
            if (bookmarkUrl) {
                fetch(bookmarkUrl, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify({ page: pageNum })
                }).then(r => r.json()).then((data) => {
                    if (data.success) {
                        const showSavedIndicator = (btn) => {
                            if (!btn) return;
                            btn.classList.add("saved");
                            const oldHtml = btn.innerHTML;
                            btn.innerHTML = '<i class="fas fa-check"></i> Bookmarked';
                            setTimeout(() => {
                                btn.classList.remove("saved");
                                btn.innerHTML = oldHtml;
                            }, 1600);
                        };
                        showSavedIndicator(bookmarkBtn);
                        showSavedIndicator(mBookmarkBtn);
                    }
                }).catch(() => {});
            }
        };

        if (bookmarkBtn) bookmarkBtn.addEventListener("click", performBookmarkAction);
        if (mBookmarkBtn) mBookmarkBtn.addEventListener("click", performBookmarkAction);

        // Themes
        document.querySelectorAll(".theme-opt-btn").forEach(btn => {
            btn.addEventListener("click", function() {
                const theme = this.dataset.theme;
                setTheme(theme);
            });
        });

        // Scrubbers
        [scrubber, mScrubber].forEach(sc => {
            if (sc) {
                sc.addEventListener("input", function() {
                    const val = parseInt(this.value, 10);
                    // Update only text labels instantly
                    if (pageNumEl) pageNumEl.textContent = val;
                    if (mobilePageNumEl) mobilePageNumEl.textContent = val;
                    if (pageInput) pageInput.value = val;
                });
                sc.addEventListener("change", function() {
                    goToPage(parseInt(this.value, 10));
                });
            }
        });

        // Direct Page Input Box
        if (pageInput) {
            pageInput.addEventListener("change", function() {
                goToPage(parseInt(this.value, 10));
            });
            pageInput.addEventListener("keydown", function(e) {
                if (e.key === "Enter") {
                    goToPage(parseInt(this.value, 10));
                    this.blur();
                }
            });
        }

        // Keyboard navigation
        document.addEventListener("keydown", (event) => {
            if (["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) return;
            if (event.key === "ArrowRight" || event.key === "PageDown") {
                goToPage(pageNum + 1);
            }
            if (event.key === "ArrowLeft" || event.key === "PageUp") {
                goToPage(pageNum - 1);
            }
            if (event.key === "Escape" && isFullscreen()) {
                exitFullscreen();
            }
        });

        // debounced resize re-fit
        let resizeTimer;
        window.addEventListener("resize", () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                if (pdfDoc) fitWidth();
            }, 220);
        });
    }

    /* ─────────────────────────────────────────
       Bootstrap
     ───────────────────────────────────────── */
    enableProtectionLayer();

    if (!window.pdfjsLib) {
        showFallback("The PDF rendering library did not load.");
        return;
    }

    pdfjsLib.GlobalWorkerOptions.workerSrc =
        "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js";

    bindControls();
    initTheme();
    renderLocalBookmarks();
    setLoaderVisible(true);

    pdfjsLib.getDocument({ url, withCredentials: true }).promise.then((pdf) => {
        pdfDoc = pdf;

        updatePageCountIndicators(pdf.numPages);

        if (Number.isNaN(pageNum) || pageNum < 1 || pageNum > pdf.numPages) {
            pageNum = 1;
        }

        setLoaderVisible(false);
        loadOutline();

        // Fit width first page
        pdf.getPage(pageNum).then((page) => {
            scale = calcFitWidthScale(page);
            scale = Math.max(0.5, Math.min(4, scale));
            renderPage(pageNum);
        });
    }).catch(() => {
        showFallback("The PDF file could not be rendered. Your reading session may have expired.");
    });
});
