export const toggleLoader = (show) => {
    const loader = document.getElementById("loader");
    if (!loader) return;
    loader.classList.toggle("hidden", !show);
};

export const storage = {
    set(key, value) {
        sessionStorage.setItem(key, JSON.stringify(value));
    },
    get(key, fallback = null) {
        const raw = sessionStorage.getItem(key);
        return raw ? JSON.parse(raw) : fallback;
    },
    remove(key) {
        sessionStorage.removeItem(key);
    },
};

export const renderCityCheckboxes = (disabled = true, homeCity = null) => {
    const container = document.getElementById("city-checkboxes");
    if (!container) return;
    container.innerHTML = "";
    "ABCDEFGHIJ".split("").forEach((city) => {
        const wrapper = document.createElement("label");
        wrapper.className =
            "flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-50 border border-blue-200 cursor-pointer hover:border-sky-500 transition";
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.value = city;
        checkbox.className = "accent-sky-500 h-4 w-4";
        checkbox.disabled = disabled;
        wrapper.appendChild(checkbox);
        const span = document.createElement("span");
        span.textContent = `City ${city}`;
        if (homeCity && city === homeCity) {
            checkbox.disabled = true;
            wrapper.classList.add("opacity-100", "bg-green-50");
            span.textContent = `City ${city} (HOME CITY)`;
            span.style.color = "green";
        }
        wrapper.appendChild(span);
        container.appendChild(wrapper);
    });
};

export const renderMatrix = (matrix) => {
    const headerRow = document.getElementById("matrix-header");
    const body = document.getElementById("matrix-body");
    if (!headerRow || !body) return;
    headerRow.innerHTML = "";
    body.innerHTML = "";
    const headerCells = ["", ...Array.from("ABCDEFGHIJ")];
    headerCells.forEach((label) => {
        const th = document.createElement("th");
        th.className = "px-2 py-1 text-sky-700 font-semibold border border-blue-200";
        th.textContent = label;
        headerRow.appendChild(th);
    });
    matrix.forEach((row, rowIdx) => {
        const tr = document.createElement("tr");
        row.forEach((cell, colIdx) => {
            if (colIdx === 0) {
                const label = document.createElement("td");
                label.className = "font-semibold text-sky-700 border border-blue-200 bg-blue-50";
                label.textContent = String.fromCharCode(65 + rowIdx);
                tr.appendChild(label);
            }
            const td = document.createElement("td");
            td.textContent = Number(cell).toFixed(1);
            td.className = "text-slate-800 border border-blue-100";
            tr.appendChild(td);
        });
        body.appendChild(tr);
    });
};

export const renderOrderControls = (cities) => {
    const container = document.getElementById("order-container");
    if (!container) return;
    container.innerHTML = "";
    cities.forEach((city, index) => {
        const wrapper = document.createElement("div");
        wrapper.className = "space-y-2";
        const label = document.createElement("label");
        label.className = "text-sm text-slate-700 block font-medium";
        label.textContent = `Visit #${index + 1}`;
        const select = document.createElement("select");
        select.className =
            "w-full rounded-lg bg-white border border-blue-200 px-3 py-2 text-slate-900 focus:border-sky-500 focus:outline-none";
        cities.forEach((optionCity) => {
            const option = document.createElement("option");
            option.value = optionCity;
            option.textContent = optionCity;
            select.appendChild(option);
        });
        select.value = city;
        wrapper.appendChild(label);
        wrapper.appendChild(select);
        container.appendChild(wrapper);
    });
};

export const getSelectedCities = () => {
    const inputs = document.querySelectorAll("#city-checkboxes input[type=checkbox]");
    return Array.from(inputs)
        .filter((box) => box.checked)
        .map((box) => box.value);
};
