/**
 * question_options.js
 * Handles dynamic option rows (add/remove/reorder) and
 * question-type switching for the question form.
 */

(function () {
    "use strict";

    // ─── Constants ──────────────────────────────────────────────
    const SINGLE_TYPES    = ["single_choice", "true_false", "fill_blank", "image_based", "quote_based"];
    const MULTI_TYPE      = "multiple_choice";
    const TF_TYPE         = "true_false";
    const IMAGE_TYPES     = ["image_based", "quote_based"];

    const typeSelect      = document.getElementById("questionTypeSelect");
    const optionsSection  = document.getElementById("optionsSection");
    const regularOptions  = document.getElementById("regularOptions");
    const tfOptions       = document.getElementById("tfOptions");
    const optionsList     = document.getElementById("optionsList");
    const imageSection    = document.getElementById("imageUploadSection");
    const singleHint      = regularOptions?.querySelector("small");

    // ─── Initial state ──────────────────────────────────────────
    let optionCounter = optionsList ? optionsList.children.length : 0;

    function getCurrentType() {
        return typeSelect ? typeSelect.value : "single_choice";
    }

    // ─── Show / hide sections based on question type ─────────────
    function applyTypeLayout(type) {
        if (!optionsSection) return;

        if (type === TF_TYPE) {
            regularOptions.style.display = "none";
            tfOptions.style.display      = "block";
        } else {
            regularOptions.style.display = "block";
            tfOptions.style.display      = "none";
        }

        // Image upload visibility
        if (imageSection) {
            imageSection.style.display = IMAGE_TYPES.includes(type) ? "block" : "none";
        }

        // Hint for single vs multi
        if (singleHint) {
            singleHint.textContent = type === MULTI_TYPE
                ? "For multiple choice, check ALL boxes that are correct."
                : "For single choice, only one "Correct" box may be checked.";
        }

        // Enforce single-correct logic when switching
        if (type !== MULTI_TYPE && type !== TF_TYPE) {
            enforceSingleCorrect();
        }
    }

    typeSelect?.addEventListener("change", () => applyTypeLayout(getCurrentType()));

    // ─── Add a new option row ────────────────────────────────────
    window.addOption = function () {
        const idx   = optionCounter++;
        const row   = document.createElement("div");
        row.className = "option-row";
        row.draggable = true;
        row.innerHTML = `
            <span class="drag-handle"><i class="fas fa-grip-vertical"></i></span>
            <input type="text" name="option_text" class="option-text-input"
                   placeholder="Option text…" required>
            <div class="option-cb-wrap">
                <input type="checkbox" name="correct_option" value="${idx}"
                       class="form-check-input correct-cb">
                <label>Correct</label>
            </div>
            <button type="button" class="option-del-btn" onclick="removeOption(this)">
                <i class="fas fa-xmark"></i>
            </button>`;

        optionsList.appendChild(row);
        attachDragListeners(row);
        attachCorrectListener(row.querySelector(".correct-cb"));
        row.querySelector(".option-text-input")?.focus();
    };

    // ─── Remove an option row ────────────────────────────────────
    window.removeOption = function (btn) {
        const row = btn.closest(".option-row");
        if (!row) return;
        if (optionsList.children.length <= 1) {
            showToast("A question needs at least one option.", "warning");
            return;
        }
        row.remove();
        reIndexCorrectValues();
    };

    // ─── Re-index checkbox values after a removal ─────────────────
    function reIndexCorrectValues() {
        Array.from(optionsList.querySelectorAll(".correct-cb")).forEach((cb, i) => {
            cb.value = i;
        });
    }

    // ─── Enforce single correct on radio-type questions ───────────
    function enforceSingleCorrect() {
        const checkboxes = optionsList.querySelectorAll(".correct-cb");
        let found = false;
        checkboxes.forEach(cb => {
            if (cb.checked && !found) {
                found = true;
            } else if (cb.checked) {
                cb.checked = false;
                cb.closest(".option-row")?.classList.remove("is-correct");
            }
        });
    }

    // ─── Correct checkbox listener ────────────────────────────────
    function attachCorrectListener(cb) {
        if (!cb) return;
        cb.addEventListener("change", () => {
            const type = getCurrentType();
            if (type !== MULTI_TYPE && type !== TF_TYPE && cb.checked) {
                // Uncheck all others
                optionsList.querySelectorAll(".correct-cb").forEach(other => {
                    if (other !== cb) {
                        other.checked = false;
                        other.closest(".option-row")?.classList.remove("is-correct");
                    }
                });
            }
            cb.closest(".option-row")?.classList.toggle("is-correct", cb.checked);
        });
    }

    // Attach to existing checkboxes on page load
    optionsList?.querySelectorAll(".correct-cb").forEach(attachCorrectListener);

    // ─── True/False selector ──────────────────────────────────────
    window.selectTF = function (value) {
        const hiddenInput = document.getElementById("tfCorrectInput");
        if (hiddenInput) hiddenInput.value = value;

        document.querySelectorAll(".tf-option").forEach(el => {
            el.classList.remove("selected-true", "selected-false");
        });

        const targetEl = value === "True"
            ? document.querySelector(".tf-option:first-child")
            : document.querySelector(".tf-option:last-child");

        if (targetEl) {
            targetEl.classList.add(value === "True" ? "selected-true" : "selected-false");
        }
    };

    // ─── Drag-and-drop reordering ─────────────────────────────────
    let dragSrc = null;

    function attachDragListeners(row) {
        row.addEventListener("dragstart", onDragStart);
        row.addEventListener("dragover",  onDragOver);
        row.addEventListener("drop",      onDrop);
        row.addEventListener("dragend",   onDragEnd);
    }

    function onDragStart(e) {
        dragSrc = this;
        e.dataTransfer.effectAllowed = "move";
        this.style.opacity = "0.5";
    }

    function onDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = "move";
        // Highlight target
        optionsList.querySelectorAll(".option-row").forEach(r => r.style.outline = "");
        this.style.outline = "2px dashed #3b82f6";
        return false;
    }

    function onDrop(e) {
        e.stopPropagation();
        if (dragSrc !== this) {
            // Swap DOM positions
            const allRows = Array.from(optionsList.children);
            const srcIdx  = allRows.indexOf(dragSrc);
            const tgtIdx  = allRows.indexOf(this);
            if (srcIdx < tgtIdx) {
                optionsList.insertBefore(dragSrc, this.nextSibling);
            } else {
                optionsList.insertBefore(dragSrc, this);
            }
            reIndexCorrectValues();
        }
        return false;
    }

    function onDragEnd() {
        this.style.opacity = "";
        optionsList.querySelectorAll(".option-row").forEach(r => r.style.outline = "");
    }

    // Attach to existing rows
    optionsList?.querySelectorAll(".option-row").forEach(attachDragListeners);

    // ─── Form validation before submit ───────────────────────────
    document.getElementById("questionForm")?.addEventListener("submit", (e) => {
        const type = getCurrentType();

        if (type === TF_TYPE) {
            // No extra validation needed
            return;
        }

        const texts    = Array.from(optionsList.querySelectorAll(".option-text-input"));
        const checkeds = Array.from(optionsList.querySelectorAll(".correct-cb:checked"));

        if (texts.length < 2) {
            e.preventDefault();
            showToast("Add at least 2 answer options.", "error");
            return;
        }

        if (checkeds.length === 0) {
            e.preventDefault();
            showToast("Mark at least one option as correct.", "error");
            return;
        }

        const empty = texts.some(t => t.value.trim() === "");
        if (empty) {
            e.preventDefault();
            showToast("All option fields must be filled in.", "error");
        }
    });

    // ─── Toast helper (fallback if not globally defined) ─────────
    function showToast(msg, type = "info") {
        if (window.showToast) {
            window.showToast(msg, type);
            return;
        }
        // Simple inline fallback
        const t = document.createElement("div");
        t.textContent = msg;
        t.style.cssText = `
            position:fixed; bottom:1.5rem; right:1.5rem; z-index:9999;
            background:${type === "error" ? "#ef4444" : "#f59e0b"};
            color:#fff; padding:.75rem 1.25rem; border-radius:10px;
            font-weight:600; font-size:.9rem; box-shadow:0 8px 24px rgba(0,0,0,.15);
            animation: fadeInUp .2s ease;
        `;
        document.body.appendChild(t);
        setTimeout(() => t.remove(), 3000);
    }

    // ─── Initial layout apply ────────────────────────────────────
    applyTypeLayout(getCurrentType());
})();
