
document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.querySelector(
        '.search-form input[name="q"]'
    );

    if (searchInput) {
        searchInput.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                searchInput.value = "";
            }
        });
    }
});
