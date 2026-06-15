document.addEventListener("DOMContentLoaded", () => {
    const root = document.getElementById("secureQuizRoot");
    if (!root) {
        return;
    }

    const attemptId = root.dataset.attemptId;
    const violationUrl = root.dataset.violationUrl;
    const autosaveUrl = root.dataset.autosaveUrl;
    const csrfToken = root.dataset.csrf;
    const requireFullscreen = root.dataset.fullscreen === "true";
    const trackFocus = root.dataset.trackFocus === "true";
    const disableCopy = root.dataset.disableCopy === "true";
    const disablePrint = root.dataset.disablePrint === "true";

    const form = document.getElementById("quizForm");
    const steps = Array.from(document.querySelectorAll(".question-step"));
    const navDots = Array.from(document.querySelectorAll(".quiz-nav-dot"));
    const btnPrev = document.getElementById("btnPrev");
    const btnNext = document.getElementById("btnNext");
    const btnSubmit = document.getElementById("btnSubmit");
    const progressText = document.getElementById("progressText");
    const progressBarFill = document.getElementById("progressBarFill");
    const saveIndicator = document.getElementById("saveIndicator");
    const cacheKey = `akhu_quiz_attempt_${attemptId}`;

    if (!form || !steps.length) {
        return;
    }

    let currentStep = 0;
    let autosaveDebounce = null;
    let lastSavedPayload = "";

    function report(type, details = "") {
        if (!violationUrl) {
            return;
        }
        fetch(violationUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify({ type, details }),
        }).catch(() => {});
    }

    function setupSecurity() {
        if (disableCopy) {
            root.style.userSelect = "none";
            root.addEventListener("contextmenu", (event) => {
                event.preventDefault();
                report("context_menu");
            });
            root.addEventListener("copy", (event) => {
                event.preventDefault();
                report("copy_attempt");
            });
            root.addEventListener("cut", (event) => {
                event.preventDefault();
                report("cut_attempt");
            });
            document.addEventListener("keydown", (event) => {
                const key = event.key.toLowerCase();
                const ctrl = event.ctrlKey || event.metaKey;
                const blocked =
                    (ctrl && ["c", "x", "v", "a", "p", "s", "u"].includes(key)) ||
                    key === "f12" ||
                    (ctrl && event.shiftKey && ["i", "j"].includes(key));
                if (blocked) {
                    event.preventDefault();
                    report("keyboard_blocked", key);
                }
            });
        }

        if (disablePrint) {
            window.addEventListener("beforeprint", (event) => {
                event.preventDefault();
                report("print_attempt");
            });
        }

        if (trackFocus) {
            document.addEventListener("visibilitychange", () => {
                if (document.hidden) {
                    report("focus_loss", "tab_hidden");
                }
            });
            window.addEventListener("blur", () => report("focus_loss", "window_blur"));
        }

        if (requireFullscreen && document.documentElement.requestFullscreen) {
            document.documentElement.requestFullscreen().catch(() => {});
            document.addEventListener("fullscreenchange", () => {
                if (!document.fullscreenElement) {
                    report("fullscreen_exit");
                }
            });
        }
    }

    function showStep(index) {
        steps.forEach((step, i) => step.classList.toggle("active", i === index));
        navDots.forEach((dot, i) => dot.classList.toggle("active", i === index));
        currentStep = index;

        if (progressText) {
            progressText.textContent = `Question ${index + 1} of ${steps.length}`;
        }
        if (progressBarFill) {
            progressBarFill.style.width = `${((index + 1) / steps.length) * 100}%`;
        }

        if (btnPrev) {
            btnPrev.style.visibility = index === 0 ? "hidden" : "visible";
        }
        if (btnNext && btnSubmit) {
            const isLast = index === steps.length - 1;
            btnNext.style.display = isLast ? "none" : "inline-flex";
            btnSubmit.style.display = isLast ? "inline-flex" : "none";
        }
    }

    function collectAnswers() {
        const data = {};
        form.querySelectorAll("input[type='radio'], input[type='checkbox']").forEach((input) => {
            if (input.checked) {
                data[input.name] = data[input.name] || [];
                data[input.name].push(input.value);
            }
        });
        return data;
    }

    function highlightSelectedOptions() {
        document.querySelectorAll(".quiz-option-label").forEach((label) => {
            const input = label.querySelector("input");
            label.classList.toggle("selected", Boolean(input?.checked));
        });
    }

    function updateDots(data = collectAnswers()) {
        steps.forEach((step, index) => {
            const container = step.querySelector(".options-container");
            const questionId = container?.dataset.questionId;
            const answered = Boolean(questionId && data[`q_${questionId}`]?.length);
            if (navDots[index]) {
                navDots[index].classList.toggle("answered", answered);
            }
        });
    }

    function setIndicator(state) {
        if (!saveIndicator) {
            return;
        }
        const labels = {
            saving: '<i class="fas fa-spinner fa-spin"></i> Saving',
            saved: '<i class="fas fa-circle-check"></i> Saved',
            local: '<i class="fas fa-circle-check"></i> Answers saved',
            error: '<i class="fas fa-triangle-exclamation"></i> Offline cache',
        };
        saveIndicator.innerHTML = labels[state] || labels.saved;
    }

    async function autosaveToServer(data) {
        if (!autosaveUrl) {
            return;
        }
        const payload = JSON.stringify(data);
        if (payload === lastSavedPayload) {
            return;
        }

        setIndicator("saving");
        try {
            const response = await fetch(autosaveUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: payload,
            });
            if (!response.ok) {
                throw new Error("Autosave failed");
            }
            lastSavedPayload = payload;
            setIndicator("saved");
        } catch (_) {
            setIndicator("error");
        }
    }

    function saveAnswers() {
        const data = collectAnswers();
        localStorage.setItem(cacheKey, JSON.stringify(data));
        highlightSelectedOptions();
        updateDots(data);

        clearTimeout(autosaveDebounce);
        autosaveDebounce = setTimeout(() => autosaveToServer(data), 1200);
    }

    function restoreAnswers() {
        const cached = localStorage.getItem(cacheKey);
        if (!cached) {
            highlightSelectedOptions();
            updateDots();
            setIndicator("local");
            return;
        }

        try {
            const data = JSON.parse(cached);
            Object.entries(data).forEach(([name, values]) => {
                values.forEach((value) => {
                    const input = form.querySelector(`input[name='${name}'][value='${value}']`);
                    if (input) {
                        input.checked = true;
                    }
                });
            });
            updateDots(data);
        } catch (_) {
            localStorage.removeItem(cacheKey);
        }

        highlightSelectedOptions();
        setIndicator("local");
    }

    function setupTimer() {
        const timerEl = document.getElementById("quizTimer");
        const timerContainer = document.getElementById("timerContainer");
        const limitMinutes = parseInt(root.dataset.timeLimit || "0", 10);
        if (!timerEl || !limitMinutes) {
            return;
        }

        let remaining = limitMinutes * 60;
        const tick = () => {
            const minutes = Math.floor(remaining / 60);
            const seconds = remaining % 60;
            timerEl.textContent = `${minutes}:${seconds.toString().padStart(2, "0")}`;

            if (remaining <= 120) {
                timerContainer?.classList.add("warning");
            }
            if (remaining <= 0) {
                localStorage.removeItem(cacheKey);
                form.submit();
                return;
            }

            remaining -= 1;
            window.setTimeout(tick, 1000);
        };
        tick();
    }

    function setupSubmitModal() {
        const confirmModal = document.getElementById("confirmModal");
        const answeredCountSpan = document.getElementById("answeredCount");
        const btnCancelSubmit = document.getElementById("btnCancelSubmit");
        const btnConfirmSubmit = document.getElementById("btnConfirmSubmit");

        btnSubmit?.addEventListener("click", () => {
            const answered = steps.filter((step) =>
                Array.from(step.querySelectorAll("input")).some((input) => input.checked)
            ).length;
            if (answeredCountSpan) {
                answeredCountSpan.textContent = answered;
            }
            confirmModal?.classList.add("active");
        });

        btnCancelSubmit?.addEventListener("click", () => confirmModal?.classList.remove("active"));
        btnConfirmSubmit?.addEventListener("click", () => {
            localStorage.removeItem(cacheKey);
            confirmModal?.classList.remove("active");
            form.submit();
        });
    }

    btnPrev?.addEventListener("click", () => {
        if (currentStep > 0) {
            showStep(currentStep - 1);
        }
    });
    btnNext?.addEventListener("click", () => {
        if (currentStep < steps.length - 1) {
            showStep(currentStep + 1);
        }
    });
    navDots.forEach((dot, index) => dot.addEventListener("click", () => showStep(index)));
    form.addEventListener("change", saveAnswers);
    window.setInterval(() => autosaveToServer(collectAnswers()), 15000);

    setupSecurity();
    restoreAnswers();
    setupTimer();
    setupSubmitModal();
    showStep(0);
});
