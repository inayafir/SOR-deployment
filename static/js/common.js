/**
 * Common JavaScript utilities for the CHSS SOR application.
 */

(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        var menuToggle = document.getElementById("menuToggle");
        var sidebar = document.getElementById("sidebar");

        if (menuToggle && sidebar) {
            menuToggle.addEventListener("click", function () {
                sidebar.classList.toggle("open");
            });

            document.addEventListener("click", function (e) {
                if (window.innerWidth <= 768 &&
                    !sidebar.contains(e.target) &&
                    !menuToggle.contains(e.target)) {
                    sidebar.classList.remove("open");
                }
            });
        }

        initDynamicSearch();
        initCategorySearch();

        document.querySelectorAll("form[data-confirm]").forEach(function (form) {
            form.addEventListener("submit", function (e) {
                if (!window.confirm(form.getAttribute("data-confirm"))) {
                    e.preventDefault();
                }
            });
        });
    });

    // ----------------------------------------------------------------------
    // Shared helpers
    // ----------------------------------------------------------------------
    function getCsrfToken() {
        var meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute("content") : "";
    }

    function escapeHtml(value) {
        return String(value).replace(/[&<>"']/g, function (ch) {
            return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch];
        });
    }

    function formatPrice(value) {
        if (value === null || value === undefined || value === "") return "";
        var num = Number(value);
        if (isNaN(num)) return "";
        return num.toLocaleString("en-US", { maximumFractionDigits: 2 });
    }

    function handleApiResponse(resp) {
        if (resp.status === 401) {
            window.location.href = "/login";
            return true;
        }
        return false;
    }

    function fetchJson(url) {
        return fetch(url, { headers: { "Accept": "application/json" } })
            .then(function (resp) {
                if (handleApiResponse(resp)) return Promise.reject("unauthorized");
                return resp.json();
            });
    }

    // Shared search state
    var searchState = {
        q: "",
        category: "",
        field: "both",
        page: 1
    };

    // Shared render function — updates the results table, count, and pagination
    function renderResults(data) {
        var countEl = document.getElementById("results-count");
        var body = document.getElementById("dataTable-body");
        var paginationEl = document.getElementById("pagination-container");
        var isManage = !!document.querySelector(".actions");

        if (countEl) {
            countEl.textContent = data.total
                ? data.total + " item" + (data.total === 1 ? "" : "s") + " found"
                : "No results";
        }

        if (body) {
            var html = "";
            if (!data.items.length) {
                html = '<tr class="no-data-row"><td colspan="' + (isManage ? 5 : 4) + '">' +
                    (searchState.q || searchState.category
                        ? "No items match your search. Try a different term or category."
                        : "No SOR items available.") +
                    "</td></tr>";
            } else {
                data.items.forEach(function (item) {
                    html += "<tr>";
                    html += '<td class="sor-code">' + escapeHtml(item.sor_code) + "</td>";
                    html += '<td title="' + escapeHtml(item.name) + '">' + escapeHtml(item.name) + "</td>";
                    html += '<td><span class="badge badge-gray">' + escapeHtml(item.category) + "</span></td>";
                    html += '<td class="text-right rate">' + formatPrice(item.price) + "</td>";
                    if (isManage) {
                        html += '<td class="text-right actions">' +
                            '<a href="/sor/' + item.id + '/edit" class="btn btn-outline btn-sm">Edit</a> ' +
                            '<form method="POST" action="/sor/' + item.id + '/delete" class="inline-form">' +
                            '<input type="hidden" name="_csrf_token" value="' + escapeHtml(getCsrfToken()) + '">' +
                            '<button type="submit" class="btn btn-danger btn-sm">Delete</button>' +
                            "</form></td>";
                    }
                    html += "</tr>";
                });
            }
            body.innerHTML = html;
        }

        if (paginationEl && data.total_pages > 1) {
            var page = data.page;
            var start = Math.max(1, page - 2);
            var end = Math.min(data.total_pages, page + 2);
            var phtml = '<nav class="pagination" aria-label="Pagination">' +
                '<div class="pagination-info">Showing ' + data.items.length + " of " + data.total + " items</div>" +
                '<div class="pagination-buttons">';
            phtml += page > 1
                ? '<a href="#" class="btn btn-outline btn-sm" data-page="' + (page - 1) + '">&laquo; Prev</a>'
                : '<span class="btn btn-outline btn-sm disabled">&laquo; Prev</span>';
            for (var p = start; p <= end; p++) {
                phtml += p === page
                    ? '<span class="btn btn-primary btn-sm">' + p + "</span>"
                    : '<a href="#" class="btn btn-outline btn-sm" data-page="' + p + '">' + p + "</a>";
            }
            phtml += page < data.total_pages
                ? '<a href="#" class="btn btn-outline btn-sm" data-page="' + (page + 1) + '">Next &raquo;</a>'
                : '<span class="btn btn-outline btn-sm disabled">Next &raquo;</span>';
            phtml += "</div></nav>";
            paginationEl.innerHTML = phtml;
        } else if (paginationEl) {
            paginationEl.innerHTML = "";
        }
    }

    // Shared fetch-and-render: builds URL params from searchState and calls renderResults
    function fetchAndRender() {
        var params = new URLSearchParams();
        if (searchState.q) params.set("q", searchState.q);
        if (searchState.category) params.set("category", searchState.category);
        if (searchState.field) params.set("field", searchState.field);
        params.set("page", searchState.page);
        fetchJson("/api/search?" + params.toString())
            .then(renderResults)
            .catch(function (err) {
                console.error("Search fetch failed:", err);
            });
    }

    // Shared function to trigger a fresh search from current searchState
    function runSearch() {
        var queryInput = document.getElementById("sor-query");
        if (queryInput) searchState.q = queryInput.value.trim();
        var fieldSelect = document.getElementById("field-select");
        if (fieldSelect) searchState.field = fieldSelect.value;
        searchState.page = 1;
        fetchAndRender();
    }

    // ----------------------------------------------------------------------
    // Category search (Google-style separate bar)
    // ----------------------------------------------------------------------
    function initCategorySearch() {
        var catInput = document.getElementById("category-search-input");
        var catBox = document.getElementById("category-autocomplete-box");
        var hiddenCat = document.getElementById("category-select");
        var categoryBar = document.getElementById("active-category-bar");
        var categoryLabel = document.getElementById("active-category-label");
        var clearCategoryBtn = document.getElementById("clear-category");
        if (!catInput || !catBox) return;

        var allCategories = [];
        var catDataEl = document.getElementById("categories-data");
        if (catDataEl) {
            try { allCategories = JSON.parse(catDataEl.textContent); } catch (e) {}
        }

        var debounceTimer = null;
        var catActiveIndex = -1;
        var catSuggestions = [];

        // Restore state
        searchState.category = hiddenCat ? hiddenCat.value : "";
        if (searchState.category && categoryBar && categoryLabel) {
            categoryLabel.textContent = searchState.category;
            categoryBar.style.display = "";
        }

        function closeCatAutocomplete() {
            catBox.innerHTML = "";
            catBox.setAttribute("aria-hidden", "true");
            catActiveIndex = -1;
            catSuggestions = [];
        }

        function setCategoryFilter(cat) {
            searchState.category = cat;
            if (hiddenCat) hiddenCat.value = cat;
            if (categoryBar && categoryLabel) {
                if (cat) {
                    categoryLabel.textContent = cat;
                    categoryBar.style.display = "";
                } else {
                    categoryBar.style.display = "none";
                }
            }
        }

        function selectCatSuggestion(cat) {
            catInput.value = cat;
            setCategoryFilter(cat);
            closeCatAutocomplete();
            runSearch();
        }

        function matchCategories(q) {
            if (!allCategories.length) return [];
            if (!q) return allCategories;
            var lower = q.toLowerCase();
            return allCategories
                .filter(function (c) { return c.toLowerCase().indexOf(lower) !== -1; });
        }

        function renderCatAutocomplete(matches) {
            catSuggestions = matches;
            if (!matches.length) {
                closeCatAutocomplete();
                return;
            }
            var html = "";
            matches.forEach(function (cat, i) {
                html += '<div class="autocomplete-item autocomplete-category" data-index="' + i + '">' +
                    '<span class="autocomplete-icon">&#128193;</span>' +
                    '<span class="autocomplete-name">' + escapeHtml(cat) + '</span>' +
                    '</div>';
            });
            catBox.innerHTML = html;
            catBox.setAttribute("aria-hidden", "false");
            catActiveIndex = -1;
        }

        function setCatActive(index) {
            var items = catBox.querySelectorAll(".autocomplete-item");
            if (index >= items.length) index = items.length - 1;
            if (index < -1) index = -1;
            catActiveIndex = index;
            for (var i = 0; i < items.length; i++) {
                items[i].classList.toggle("active", i === index);
            }
        }

        // Events
        catInput.addEventListener("focus", function () {
            var q = catInput.value.trim();
            var matches = matchCategories(q);
            renderCatAutocomplete(matches);
        });

        catInput.addEventListener("input", function () {
            clearTimeout(debounceTimer);
            var q = catInput.value.trim();
            debounceTimer = setTimeout(function () {
                var matches = matchCategories(q);
                renderCatAutocomplete(matches);
            }, 150);
        });

        catInput.addEventListener("keydown", function (e) {
            if (e.key === "Escape") {
                closeCatAutocomplete();
                return;
            }
            if (!catSuggestions.length) return;
            if (e.key === "ArrowDown") {
                e.preventDefault();
                setCatActive(catActiveIndex + 1);
            } else if (e.key === "ArrowUp") {
                e.preventDefault();
                setCatActive(catActiveIndex - 1);
            } else if (e.key === "Enter" && catActiveIndex >= 0) {
                e.preventDefault();
                selectCatSuggestion(catSuggestions[catActiveIndex]);
            } else if (e.key === "Enter" && catActiveIndex === -1) {
                e.preventDefault();
                setCategoryFilter(catInput.value.trim());
                closeCatAutocomplete();
                runSearch();
            }
        });

        // Use mousedown + preventDefault to select items before blur fires
        catBox.addEventListener("mousedown", function (e) {
            e.preventDefault();
            var el = e.target.closest(".autocomplete-item");
            if (!el) return;
            var idx = parseInt(el.getAttribute("data-index"), 10);
            if (catSuggestions[idx]) {
                selectCatSuggestion(catSuggestions[idx]);
            }
        });

        catInput.addEventListener("blur", function () {
            setTimeout(function () {
                closeCatAutocomplete();
            }, 150);
        });

        if (clearCategoryBtn) {
            clearCategoryBtn.addEventListener("click", function () {
                catInput.value = "";
                setCategoryFilter("");
                runSearch();
            });
        }
    }

    // ----------------------------------------------------------------------
    // SOR item search (existing autocomplete)
    // ----------------------------------------------------------------------
    function initDynamicSearch() {
        var queryInput = document.getElementById("sor-query");
        if (!queryInput) return;

        var autocompleteBox = document.getElementById("autocomplete-box");
        var searchForm = document.getElementById("search-form");
        var fieldSelect = document.getElementById("field-select");

        var debounceMs = 250;
        var debounceTimer = null;
        var activeIndex = -1;
        var suggestions = [];

        searchState.q = queryInput.value.trim();

        function closeAutocomplete() {
            autocompleteBox.innerHTML = "";
            autocompleteBox.setAttribute("aria-hidden", "true");
            activeIndex = -1;
            suggestions = [];
        }

        function openAutocomplete(items) {
            suggestions = items;
            if (!items.length) {
                closeAutocomplete();
                return;
            }
            var html = "";
            items.forEach(function (item, i) {
                html += '<div class="autocomplete-item" data-index="' + i + '">' +
                    '<span class="autocomplete-name">' + escapeHtml(item.name) + "</span>" +
                    '<span class="autocomplete-code">' + escapeHtml(item.sor_code) + "</span>" +
                    '<span class="autocomplete-meta">' + escapeHtml(item.category) + "</span>" +
                    '<span class="autocomplete-price">&#8377; ' + formatPrice(item.price) + "</span></div>";
            });
            autocompleteBox.innerHTML = html;
            autocompleteBox.setAttribute("aria-hidden", "false");
            activeIndex = -1;
        }

        function setActive(index) {
            var items = autocompleteBox.querySelectorAll(".autocomplete-item");
            if (index >= items.length) index = items.length - 1;
            if (index < -1) index = -1;
            activeIndex = index;
            for (var i = 0; i < items.length; i++) {
                items[i].classList.toggle("active", i === index);
            }
        }

        function selectSuggestion(item) {
            if (!item) return;
            queryInput.value = item.name;
            closeAutocomplete();
            searchState.q = item.name;
            searchState.page = 1;
            fetchAndRender();
        }

        function fetchSuggestions() {
            var q = queryInput.value.trim();
            if (!q) { closeAutocomplete(); return; }
            var params = new URLSearchParams({ q: q });
            if (searchState.field) params.set("field", searchState.field);
            fetchJson("/api/suggest?" + params.toString())
                .then(function (data) { openAutocomplete(data.items); })
                .catch(function () {});
        }

        // Events
        queryInput.addEventListener("input", function () {
            clearTimeout(debounceTimer);
            searchState.q = queryInput.value.trim();
            debounceTimer = setTimeout(function () {
                fetchSuggestions();
                searchState.page = 1;
                fetchAndRender();
            }, debounceMs);
        });

        queryInput.addEventListener("keydown", function (e) {
            if (e.key === "Escape") { closeAutocomplete(); return; }
            if (!suggestions.length) return;
            if (e.key === "ArrowDown") { e.preventDefault(); setActive(activeIndex + 1); }
            else if (e.key === "ArrowUp") { e.preventDefault(); setActive(activeIndex - 1); }
            else if (e.key === "Enter" && activeIndex >= 0) { e.preventDefault(); selectSuggestion(suggestions[activeIndex]); }
        });

        autocompleteBox.addEventListener("click", function (e) {
            var el = e.target.closest(".autocomplete-item");
            if (!el) return;
            selectSuggestion(suggestions[parseInt(el.getAttribute("data-index"), 10)]);
        });

        if (searchForm) {
            searchForm.addEventListener("submit", function (e) {
                e.preventDefault();
                closeAutocomplete();
                searchState.q = queryInput.value.trim();
                searchState.page = 1;
                fetchAndRender();
            });
        }

        if (fieldSelect) {
            fieldSelect.addEventListener("change", function () {
                searchState.field = fieldSelect.value;
                if (queryInput.value.trim()) fetchSuggestions();
                searchState.page = 1;
                fetchAndRender();
            });
        }

        document.addEventListener("click", function (e) {
            if (!e.target.closest(".sor-autocomplete")) closeAutocomplete();
        });
    }
})();
