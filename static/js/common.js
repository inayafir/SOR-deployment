/**
 * Common JavaScript utilities for the CHSS SOR application.
 */

(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        // Mobile sidebar toggle
        var menuToggle = document.getElementById("menuToggle");
        var sidebar = document.getElementById("sidebar");

        if (menuToggle && sidebar) {
            menuToggle.addEventListener("click", function () {
                sidebar.classList.toggle("open");
            });

            // Close sidebar when clicking outside on mobile
            document.addEventListener("click", function (e) {
                if (window.innerWidth <= 768 &&
                    !sidebar.contains(e.target) &&
                    !menuToggle.contains(e.target)) {
                    sidebar.classList.remove("open");
                }
            });
        }

        initDynamicSearch();

        // Confirmation dialogs for destructive forms (data-confirm="message")
        document.querySelectorAll("form[data-confirm]").forEach(function (form) {
            form.addEventListener("submit", function (e) {
                if (!window.confirm(form.getAttribute("data-confirm"))) {
                    e.preventDefault();
                }
            });
        });
    });

    // ----------------------------------------------------------------------
    // Dynamic search + autocomplete (Search & Manage pages)
    // ----------------------------------------------------------------------
    function initDynamicSearch() {
        var queryInput = document.getElementById("sor-query");
        if (!queryInput) {
            return;
        }

        var body = document.getElementById("dataTable-body");
        var countEl = document.getElementById("results-count");
        var paginationEl = document.getElementById("pagination-container");
        var categorySelect = document.getElementById("category-select");
        var fieldSelect = document.getElementById("field-select");
        var autocompleteBox = document.getElementById("autocomplete-box");
        var searchForm = document.getElementById("search-form");
        var isManage = !!document.querySelector(".actions");

        var csrfToken = getCsrfToken();
        var debounceMs = 250;
        var debounceTimer = null;
        var activeIndex = -1;
        var suggestions = [];
        var state = {
            q: queryInput.value.trim(),
            category: categorySelect ? categorySelect.value : "",
            field: fieldSelect ? fieldSelect.value : "both",
            page: 1
        };

        function getCsrfToken() {
            var meta = document.querySelector('meta[name="csrf-token"]');
            return meta ? meta.getAttribute("content") : "";
        }

        function escapeHtml(value) {
            return String(value).replace(/[&<>"']/g, function (ch) {
                return {
                    "&": "&amp;",
                    "<": "&lt;",
                    ">": "&gt;",
                    '"': "&quot;",
                    "'": "&#39;"
                }[ch];
            });
        }

        function formatPrice(value) {
            if (value === null || value === undefined || value === "") {
                return "";
            }
            var num = Number(value);
            if (isNaN(num)) {
                return "";
            }
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
                    if (handleApiResponse(resp)) {
                        return Promise.reject("unauthorized");
                    }
                    return resp.json();
                });
        }

        // ------------------------------------------------------------------
        // Results
        // ------------------------------------------------------------------
        function buildSearchUrl(page) {
            var params = new URLSearchParams();
            if (state.q) {
                params.set("q", state.q);
            }
            if (state.category) {
                params.set("category", state.category);
            }
            if (state.field) {
                params.set("field", state.field);
            }
            params.set("page", page);
            return "/api/search?" + params.toString();
        }

        function runSearch(page) {
            state.page = page || 1;
            fetchJson(buildSearchUrl(state.page)).then(renderResults).catch(function () {});
        }

        function renderResults(data) {
            renderCount(data);
            renderRows(data);
            renderPagination(data);
        }

        function renderCount(data) {
            countEl.textContent = data.total
                ? data.total + " item" + (data.total === 1 ? "" : "s") + " found"
                : "No results";
        }

        function renderRows(data) {
            var html = "";
            if (!data.items.length) {
                html = '<tr class="no-data-row"><td colspan="' +
                    (isManage ? 5 : 4) + '">' +
                    (state.q || state.category
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
                            '<input type="hidden" name="_csrf_token" value="' + escapeHtml(csrfToken) + '">' +
                            '<button type="submit" class="btn btn-danger btn-sm">Delete</button>' +
                            "</form></td>";
                    }
                    html += "</tr>";
                });
            }
            body.innerHTML = html;
        }

        function paginationButton(page, label) {
            return '<a href="#" class="btn btn-outline btn-sm" data-page="' + page + '">' + label + "</a>";
        }

        function renderPagination(data) {
            if (data.total_pages <= 1) {
                paginationEl.innerHTML = "";
                return;
            }
            var page = data.page;
            var start = Math.max(1, page - 2);
            var end = Math.min(data.total_pages, page + 2);
            var html = '<nav class="pagination" aria-label="Pagination">' +
                '<div class="pagination-info">Showing ' + data.items.length + " of " + data.total + " items</div>" +
                '<div class="pagination-buttons">';

            html += page > 1
                ? paginationButton(page - 1, "&laquo; Prev")
                : '<span class="btn btn-outline btn-sm disabled">&laquo; Prev</span>';

            for (var p = start; p <= end; p++) {
                html += p === page
                    ? '<span class="btn btn-primary btn-sm">' + p + "</span>"
                    : paginationButton(p, String(p));
            }

            html += page < data.total_pages
                ? paginationButton(page + 1, "Next &raquo;")
                : '<span class="btn btn-outline btn-sm disabled">Next &raquo;</span>';

            html += "</div></nav>";
            paginationEl.innerHTML = html;
        }

        // ------------------------------------------------------------------
        // Autocomplete
        // ------------------------------------------------------------------
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
            if (index >= items.length) {
                index = items.length - 1;
            }
            if (index < -1) {
                index = -1;
            }
            activeIndex = index;
            for (var i = 0; i < items.length; i++) {
                items[i].classList.toggle("active", i === index);
            }
        }

        function syncSelects() {
            if (categorySelect) {
                state.category = categorySelect.value;
            }
            if (fieldSelect) {
                state.field = fieldSelect.value;
            }
        }

        function selectSuggestion(item) {
            if (!item) {
                return;
            }
            queryInput.value = item.name;
            closeAutocomplete();
            state.q = item.name;
            syncSelects();
            runSearch(1);
        }

        function fetchSuggestions() {
            var q = queryInput.value.trim();
            if (!q) {
                closeAutocomplete();
                return;
            }
            var params = new URLSearchParams({ q: q });
            if (state.field) {
                params.set("field", state.field);
            }
            fetchJson("/api/suggest?" + params.toString())
                .then(function (data) {
                    openAutocomplete(data.items);
                })
                .catch(function () {});
        }

        // ------------------------------------------------------------------
        // Event wiring
        // ------------------------------------------------------------------
        queryInput.addEventListener("input", function () {
            clearTimeout(debounceTimer);
            state.q = queryInput.value.trim();
            syncSelects();
            debounceTimer = setTimeout(function () {
                fetchSuggestions();
                runSearch(1);
            }, debounceMs);
        });

        queryInput.addEventListener("keydown", function (e) {
            if (e.key === "Escape") {
                closeAutocomplete();
                return;
            }
            if (!suggestions.length) {
                return;
            }
            if (e.key === "ArrowDown") {
                e.preventDefault();
                setActive(activeIndex + 1);
            } else if (e.key === "ArrowUp") {
                e.preventDefault();
                setActive(activeIndex - 1);
            } else if (e.key === "Enter" && activeIndex >= 0) {
                e.preventDefault();
                selectSuggestion(suggestions[activeIndex]);
            }
        });

        autocompleteBox.addEventListener("click", function (e) {
            var el = e.target.closest(".autocomplete-item");
            if (!el) {
                return;
            }
            selectSuggestion(suggestions[parseInt(el.getAttribute("data-index"), 10)]);
        });

        if (searchForm) {
            searchForm.addEventListener("submit", function (e) {
                e.preventDefault();
                closeAutocomplete();
                state.q = queryInput.value.trim();
                syncSelects();
                runSearch(1);
            });
        }

        if (categorySelect) {
            categorySelect.addEventListener("change", function () {
                syncSelects();
                runSearch(1);
            });
        }

        if (fieldSelect) {
            fieldSelect.addEventListener("change", function () {
                syncSelects();
                if (queryInput.value.trim()) {
                    fetchSuggestions();
                }
                runSearch(1);
            });
        }

        if (paginationEl) {
            paginationEl.addEventListener("click", function (e) {
                var link = e.target.closest("a[data-page]");
                if (!link) {
                    return;
                }
                e.preventDefault();
                runSearch(parseInt(link.getAttribute("data-page"), 10));
            });
        }

        if (body) {
            body.addEventListener("submit", function (e) {
                var form = e.target;
                if (!form.classList || !form.classList.contains("inline-form")) {
                    return;
                }
                var row = form.closest("tr");
                var code = row ? row.cells[0].textContent.trim() : "this";
                if (!window.confirm("Delete SOR item " + code + "?")) {
                    e.preventDefault();
                }
            });
        }

        document.addEventListener("click", function (e) {
            if (!e.target.closest(".sor-autocomplete")) {
                closeAutocomplete();
            }
        });
    }
})();
