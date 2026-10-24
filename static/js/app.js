// HydroGuard AI Dashboard Client Logic

let map;
let hazardCircle;
let trendChart;
let currentReportMd = "";
let currentCityName = "HydroGuard AI Report";
let lastTelemetryData = null; // Store last fetched data to use as context for chat/translations

// Initialize Dashboard components on DOM load
document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initMap();
    initChart();
    loadPresets();
    setupEventHandlers();
    setupAutocomplete();
    
    // Auto-trigger default search on Venice
    setTimeout(() => {
        triggerPresetSearch("venice");
    }, 500);
});

// 1. Initialize Theme (Light/Dark Mode Check)
function initTheme() {
    const savedTheme = localStorage.getItem("theme") || "dark";
    if (savedTheme === "light") {
        document.body.classList.add("light-theme");
    } else {
        document.body.classList.remove("light-theme");
    }
}

// 2. Initialize Leaflet Map
function initMap() {
    map = L.map('leafletMap', {
        zoomControl: false,
        attributionControl: false
    }).setView([20, 0], 2);

    // Dark styled tile layer via OSM
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
    }).addTo(map);

    L.control.zoom({
        position: 'topright'
    }).addTo(map);
}

// 3. Initialize Empty Chart.js Instance
function initChart() {
    const ctx = document.getElementById('trendChart').getContext('2d');
    const isLight = document.body.classList.contains("light-theme");
    
    // Config values based on theme state
    const gridColor = isLight ? 'rgba(15, 23, 42, 0.05)' : 'rgba(255, 255, 255, 0.03)';
    const tickColor = isLight ? '#475569' : '#94a3b8';

    trendChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
            datasets: [
                {
                    label: 'Precipitation Forecast (mm)',
                    data: [0, 0, 0, 0, 0, 0, 0],
                    backgroundColor: 'rgba(59, 130, 246, 0.4)',
                    borderColor: '#3b82f6',
                    borderWidth: 1.5,
                    yAxisID: 'yRain',
                    borderRadius: 4
                },
                {
                    label: 'River Discharge (m³/s)',
                    data: [0, 0, 0, 0, 0, 0, 0],
                    type: 'line',
                    borderColor: '#00e0ff',
                    backgroundColor: 'rgba(0, 224, 255, 0.05)',
                    borderWidth: 3,
                    pointBackgroundColor: '#00e0ff',
                    pointHoverRadius: 7,
                    tension: 0.3,
                    yAxisID: 'yFlow'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: tickColor,
                        font: { family: 'Outfit', size: 11 }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(7, 10, 19, 0.9)',
                    titleFont: { family: 'Outfit', weight: 'bold' },
                    bodyFont: { family: 'JetBrains Mono' },
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: { color: gridColor },
                    ticks: { color: tickColor, font: { family: 'Outfit' } }
                },
                yRain: {
                    type: 'linear',
                    position: 'left',
                    grid: { color: gridColor },
                    ticks: { color: tickColor, font: { family: 'Outfit' } },
                    title: {
                        display: true,
                        text: 'Daily Rain (mm)',
                        color: '#3b82f6',
                        font: { family: 'Outfit', weight: 'bold' }
                    }
                },
                yFlow: {
                    type: 'linear',
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    ticks: { color: tickColor, font: { family: 'Outfit' } },
                    title: {
                        display: true,
                        text: 'Discharge Rate (m³/s)',
                        color: '#00e0ff',
                        font: { family: 'Outfit', weight: 'bold' }
                    }
                }
            }
        }
    });
}

// 4. Load Presets
function loadPresets() {
    const container = document.getElementById("presetsContainer");
    
    fetch("/api/presets")
        .then(res => res.json())
        .then(presets => {
            container.innerHTML = "";
            
            Object.keys(presets).forEach(key => {
                const preset = presets[key];
                const btn = document.createElement("button");
                btn.className = "preset-btn";
                btn.id = `preset-${key}`;
                btn.innerText = preset.name;
                btn.title = preset.description;
                btn.onclick = () => triggerPresetSearch(key, preset);
                container.appendChild(btn);
            });
        })
        .catch(err => {
            console.error("Error loading presets:", err);
            container.innerHTML = `<span style="color: var(--color-extreme); font-size: 12px;"><i class="fa-solid fa-triangle-exclamation"></i> Presets failed to load</span>`;
        });
}

// 5. Setup Event Handlers
function setupEventHandlers() {
    // Search Form Submit
    const searchForm = document.getElementById("searchForm");
    searchForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const query = document.getElementById("locationInput").value.trim();
        if (query) {
            document.querySelectorAll(".preset-btn").forEach(b => b.classList.remove("active"));
            fetchTelemetryData(`/api/summary?location=${encodeURIComponent(query)}`);
            document.getElementById("searchAutocompleteList").classList.add("hidden");
        }
    });

    // Language Selector
    const langSelect = document.getElementById("langSelect");
    langSelect.addEventListener("change", () => {
        if (lastTelemetryData) {
            const lat = lastTelemetryData.location.latitude;
            const lon = lastTelemetryData.location.longitude;
            const name = lastTelemetryData.location.name;
            const lang = langSelect.value;
            fetchTelemetryData(`/api/summary?lat=${lat}&lon=${lon}&name=${encodeURIComponent(name)}&lang=${lang}`);
        }
    });

    // Theme Toggle Button
    const themeBtn = document.getElementById("themeToggleBtn");
    themeBtn.addEventListener("click", () => {
        const isLight = document.body.classList.toggle("light-theme");
        localStorage.setItem("theme", isLight ? "light" : "dark");
        
        // Update Chart ticks & legend labels for contrast
        const gridColor = isLight ? 'rgba(15, 23, 42, 0.05)' : 'rgba(255, 255, 255, 0.03)';
        const tickColor = isLight ? '#475569' : '#94a3b8';
        
        trendChart.options.scales.x.grid.color = gridColor;
        trendChart.options.scales.x.ticks.color = tickColor;
        trendChart.options.scales.yRain.grid.color = gridColor;
        trendChart.options.scales.yRain.ticks.color = tickColor;
        trendChart.options.scales.yFlow.ticks.color = tickColor;
        trendChart.options.plugins.legend.labels.color = tickColor;
        trendChart.update();
    });

    // GPS Locate Me Button
    const gpsBtn = document.getElementById("gpsButton");
    gpsBtn.addEventListener("click", () => {
        if (!navigator.geolocation) {
            alert("Geolocation is not supported by your browser.");
            return;
        }
        
        gpsBtn.querySelector("i").className = "fa-solid fa-spinner fa-spin";
        
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;
                const lang = langSelect.value;
                document.getElementById("locationInput").value = `GPS Coordinates: ${lat.toFixed(4)}, ${lon.toFixed(4)}`;
                fetchTelemetryData(`/api/summary?lat=${lat}&lon=${lon}&name=GPS%20Location&lang=${lang}`);
                document.querySelectorAll(".preset-btn").forEach(b => b.classList.remove("active"));
                gpsBtn.querySelector("i").className = "fa-solid fa-location-crosshairs";
            },
            (err) => {
                console.error("GPS error:", err);
                alert(`GPS Error: ${err.message}. Please check location permissions.`);
                gpsBtn.querySelector("i").className = "fa-solid fa-location-crosshairs";
            },
            { enableHighAccuracy: true, timeout: 8000 }
        );
    });

    // Expandable Manual Coordinates panel
    const toggleCoordsBtn = document.getElementById("toggleCoordsBtn");
    const coordsForm = document.getElementById("coordsForm");
    const coordsArrow = document.getElementById("coordsArrow");
    
    toggleCoordsBtn.addEventListener("click", () => {
        const isHidden = coordsForm.classList.toggle("hidden");
        coordsArrow.classList.toggle("rotated", !isHidden);
    });

    // Coordinates Form submit
    coordsForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const latRaw = document.getElementById("latInput").value.trim();
        const lonRaw = document.getElementById("lonInput").value.trim();
        const nameVal = document.getElementById("nameInput").value.trim();
        const lang = langSelect.value;

        const latVal = parseFloat(latRaw);
        const lonVal = parseFloat(lonRaw);

        // Fallback: If Lat/Lon are left empty but Name is provided, geocode it
        if ((latRaw === "" || lonRaw === "" || isNaN(latVal) || isNaN(lonVal))) {
            if (nameVal !== "") {
                // Trigger geocoding fetch for the name
                fetch(`/api/search?q=${encodeURIComponent(nameVal)}`)
                    .then(res => res.json())
                    .then(matches => {
                        if (matches && matches.length > 0) {
                            const match = matches[0];
                            // Fill out inputs so user sees resolved values
                            document.getElementById("latInput").value = match.latitude.toFixed(4);
                            document.getElementById("lonInput").value = match.longitude.toFixed(4);
                            document.getElementById("locationInput").value = match.full_name;

                            fetchTelemetryData(`/api/summary?lat=${match.latitude}&lon=${match.longitude}&name=${encodeURIComponent(match.full_name)}&lang=${lang}`);
                            document.querySelectorAll(".preset-btn").forEach(b => b.classList.remove("active"));
                            
                            // Hide coordinates panel
                            coordsForm.classList.add("hidden");
                            coordsArrow.classList.remove("rotated");
                        } else {
                            alert(`Could not resolve location name "${nameVal}". Please check the spelling or input coordinates manually.`);
                        }
                    })
                    .catch(err => {
                        console.error("Geocoding coordinates fallback failed:", err);
                        alert("Geocoding service unavailable. Please check coordinates manually.");
                    });
            } else {
                alert("Please enter either numerical Latitude/Longitude coordinates or a Location Name.");
            }
            return;
        }

        const resolvedName = nameVal || `Coordinate: ${latVal.toFixed(4)}, ${lonVal.toFixed(4)}`;
        document.getElementById("locationInput").value = resolvedName;
        
        fetchTelemetryData(`/api/summary?lat=${latVal}&lon=${lonVal}&name=${encodeURIComponent(resolvedName)}&lang=${lang}`);
        document.querySelectorAll(".preset-btn").forEach(b => b.classList.remove("active"));
        
        // Hide panel
        coordsForm.classList.add("hidden");
        coordsArrow.classList.remove("rotated");
    });

    // Tab Navigation Switcher
    const tabs = document.querySelectorAll(".tab-link");
    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");
            
            const targetTab = tab.getAttribute("data-tab");
            document.querySelectorAll(".tab-content").forEach(tc => tc.classList.remove("active"));
            document.getElementById(targetTab).classList.add("active");
            
            if (targetTab === "dashboardTab") {
                setTimeout(() => { map.invalidateSize(); }, 200);
            }
        });
    });

    // Copy / Download report logic
    const btnCopy = document.getElementById("btnCopyReport");
    btnCopy.addEventListener("click", () => {
        if (!currentReportMd) return;
        navigator.clipboard.writeText(currentReportMd).then(() => {
            btnCopy.innerHTML = `<i class="fa-solid fa-check" style="color: var(--color-low);"></i>`;
            setTimeout(() => { btnCopy.innerHTML = `<i class="fa-regular fa-copy"></i>`; }, 2000);
        });
    });

    const btnDownload = document.getElementById("btnDownloadReport");
    btnDownload.addEventListener("click", () => {
        if (!currentReportMd) return;
        const blob = new Blob([currentReportMd], { type: "text/markdown;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        const cleanName = currentCityName.replace(/[^a-z0-9]/gi, '_').toLowerCase();
        link.setAttribute("download", `${cleanName}_flood_warning.md`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    });

    // AI Safety Assistant Form
    const chatForm = document.getElementById("chatForm");
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        submitUserChatMessage();
    });

    // AI Chat Suggested Chip clicks
    const promptChips = document.querySelectorAll(".prompt-chip");
    promptChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const promptText = chip.getAttribute("data-prompt");
            document.getElementById("chatInput").value = promptText;
            submitUserChatMessage();
        });
    });
}

// 6. Geocoding Search Autocomplete Debouncing
function setupAutocomplete() {
    const input = document.getElementById("locationInput");
    const dropdown = document.getElementById("searchAutocompleteList");
    let debounceTimer;
    let selectedIndex = -1;
    let totalItems = 0;

    function highlightMatch(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<strong>$1</strong>');
    }

    input.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        const val = input.value.trim();
        selectedIndex = -1;

        if (val.length < 2) {
            dropdown.classList.add("hidden");
            return;
        }

        // Wait 300ms after user stops typing to trigger request
        debounceTimer = setTimeout(() => {
            fetch(`/api/search?q=${encodeURIComponent(val)}`)
                .then(res => res.json())
                .then(matches => {
                    dropdown.innerHTML = "";
                    
                    if (!matches || matches.length === 0) {
                        const noMatch = document.createElement("div");
                        noMatch.className = "autocomplete-item no-match";
                        noMatch.textContent = "No matching state or city found";
                        noMatch.style.pointerEvents = "none";
                        noMatch.style.opacity = "0.6";
                        dropdown.appendChild(noMatch);
                        dropdown.classList.remove("hidden");
                        totalItems = 0;
                        return;
                    }

                    totalItems = matches.length;
                    matches.forEach((item, idx) => {
                        const row = document.createElement("div");
                        row.className = "autocomplete-item";
                        row.setAttribute("data-index", idx);
                        
                        const highlightedName = highlightMatch(escapeHTML(item.name), val);
                        const highlightedFull = highlightMatch(escapeHTML(item.full_name), val);
                        
                        row.innerHTML = `
                            <i class="fa-solid fa-location-dot"></i>
                            <div>
                                <span class="loc-name">${highlightedName}</span>
                                <div class="loc-details">${highlightedFull}</div>
                            </div>
                        `;
                        
                        row.addEventListener("click", () => {
                            input.value = item.full_name;
                            dropdown.classList.add("hidden");
                            
                            const lang = document.getElementById("langSelect").value;
                            fetchTelemetryData(`/api/summary?lat=${item.latitude}&lon=${item.longitude}&name=${encodeURIComponent(item.full_name)}&lang=${lang}`);
                            document.querySelectorAll(".preset-btn").forEach(b => b.classList.remove("active"));
                        });

                        row.addEventListener("mouseenter", () => {
                            document.querySelectorAll(".autocomplete-item").forEach(item => item.classList.remove("selected"));
                            row.classList.add("selected");
                            selectedIndex = idx;
                        });

                        dropdown.appendChild(row);
                    });
                    dropdown.classList.remove("hidden");
                })
                .catch(err => {
                    console.error("Autocomplete geocode failed:", err);
                });
        }, 300);
    });

    input.addEventListener("keydown", (e) => {
        const items = dropdown.querySelectorAll(".autocomplete-item:not(.no-match)");
        
        if (e.key === "ArrowDown") {
            e.preventDefault();
            selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
            updateSelection(items);
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            selectedIndex = Math.max(selectedIndex - 1, -1);
            if (selectedIndex === -1) {
                items.forEach(item => item.classList.remove("selected"));
            } else {
                updateSelection(items);
            }
        } else if (e.key === "Enter") {
            e.preventDefault();
            if (selectedIndex >= 0 && selectedIndex < items.length) {
                items[selectedIndex].click();
            }
        } else if (e.key === "Escape") {
            dropdown.classList.add("hidden");
        }
    });

    function updateSelection(items) {
        items.forEach(item => item.classList.remove("selected"));
        if (selectedIndex >= 0 && selectedIndex < items.length) {
            items[selectedIndex].classList.add("selected");
            items[selectedIndex].scrollIntoView({ block: "nearest" });
        }
    }

    // Close autocomplete menu when clicking outside search area
    document.addEventListener("click", (e) => {
        if (!e.target.closest(".search-section")) {
            dropdown.classList.add("hidden");
        }
    });
}

// 7. Submit Chat message
function submitUserChatMessage() {
    const input = document.getElementById("chatInput");
    const log = document.getElementById("chatLog");
    const prompt = input.value.trim();
    if (!prompt) return;

    input.value = "";

    const userMsg = document.createElement("div");
    userMsg.className = "chat-message user";
    userMsg.innerHTML = `<div class="msg-bubble"><p>${escapeHTML(prompt)}</p></div>`;
    log.appendChild(userMsg);
    log.scrollTop = log.scrollHeight;

    const typingIndicator = document.createElement("div");
    typingIndicator.className = "chat-message bot typing-loader";
    typingIndicator.innerHTML = `
        <div class="msg-bubble">
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    log.appendChild(typingIndicator);
    log.scrollTop = log.scrollHeight;

    const context = {
        location_name: lastTelemetryData ? lastTelemetryData.location.name : "Unknown Location",
        risk_level: lastTelemetryData ? lastTelemetryData.risk_level : "NORMAL",
        risk_score: lastTelemetryData ? lastTelemetryData.risk_score : 0.0,
        precipitation: lastTelemetryData ? lastTelemetryData.metrics.total_precip_7d : 0.0,
        discharge: lastTelemetryData ? lastTelemetryData.metrics.peak_discharge : null
    };

    fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: prompt, context: context })
    })
    .then(res => res.json())
    .then(data => {
        typingIndicator.remove();
        
        const botMsg = document.createElement("div");
        botMsg.className = "chat-message bot";
        
        let parsedResponse = data.response;
        if (typeof marked !== 'undefined') {
            parsedResponse = marked.parse(data.response);
        } else {
            parsedResponse = `<p>${escapeHTML(data.response)}</p>`;
        }
        
        botMsg.innerHTML = `<div class="msg-bubble">${parsedResponse}</div>`;
        log.appendChild(botMsg);
        log.scrollTop = log.scrollHeight;
    })
    .catch(err => {
        console.error("Chat error:", err);
        typingIndicator.remove();
        
        const errorMsg = document.createElement("div");
        errorMsg.className = "chat-message bot";
        errorMsg.innerHTML = `<div class="msg-bubble"><p style="color: var(--color-extreme);"><i class="fa-solid fa-triangle-exclamation"></i> Failed to compile assistant response. Please check network connection.</p></div>`;
        log.appendChild(errorMsg);
        log.scrollTop = log.scrollHeight;
    });
}

function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}

function triggerPresetSearch(key, presetData) {
    document.querySelectorAll(".preset-btn").forEach(btn => {
        if (btn.id === `preset-${key}`) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });
    
    const lang = document.getElementById("langSelect").value;
    
    if (presetData) {
        document.getElementById("locationInput").value = presetData.name;
        fetchTelemetryData(`/api/summary?lat=${presetData.lat}&lon=${presetData.lon}&name=${encodeURIComponent(presetData.name)}&lang=${lang}`);
    } else {
        fetch(`/api/presets`)
            .then(res => res.json())
            .then(presets => {
                const data = presets[key];
                if (data) {
                    document.getElementById("locationInput").value = data.name;
                    fetchTelemetryData(`/api/summary?lat=${data.lat}&lon=${data.lon}&name=${encodeURIComponent(data.name)}&lang=${lang}`);
                }
            });
    }
}

// 8. Fetch Telemetry
function fetchTelemetryData(apiUrl) {
    const overlay = document.getElementById("loadingOverlay");
    const searchBtn = document.getElementById("searchButton");
    
    overlay.classList.remove("hidden");
    searchBtn.disabled = true;
    searchBtn.querySelector("span").innerText = "Analyzing...";
    searchBtn.querySelector("i").className = "fa-solid fa-spinner button-loader";
    searchBtn.querySelector("i").style.display = "inline-block";

    fetch(apiUrl)
        .then(res => {
            if (!res.ok) {
                return res.json().then(errData => {
                    throw new Error(errData.error || "Failed to fetch dashboard metrics.");
                });
            }
            return res.json();
        })
        .then(data => {
            lastTelemetryData = data;
            updateDashboardUI(data);
        })
        .catch(err => {
            console.error("Telemetry fetch error:", err);
            alert(`Analysis Error: ${err.message}`);
        })
        .finally(() => {
            overlay.classList.add("hidden");
            searchBtn.disabled = false;
            searchBtn.querySelector("span").innerText = "Analyze";
            searchBtn.querySelector("i").className = "fa-solid fa-chart-line button-loader";
            searchBtn.querySelector("i").style.display = "none";
        });
}

// 9. Update Dashboard UI widgets
function updateDashboardUI(data) {
    currentReportMd = data.summary_markdown;
    currentCityName = data.location.name;
    
    const tickerContainer = document.getElementById("calamityTickerContainer");
    const tickerText = document.getElementById("calamityTickerText");
    
    if (data.calamity_alert) {
        tickerText.innerText = data.calamity_alert;
        tickerContainer.classList.remove("hidden");
    } else {
        tickerContainer.classList.add("hidden");
    }
    
    document.getElementById("chatContextText").innerText = `Active Scan Location: ${data.location.name} (${data.risk_level})`;

    document.getElementById("locationName").innerText = data.location.name;
    document.getElementById("locationCoordinates").innerText = 
        `LAT: ${data.location.latitude.toFixed(4)} | LON: ${data.location.longitude.toFixed(4)}`;
    
    const riskScoreEl = document.getElementById("riskScore");
    const riskLevelTextEl = document.getElementById("riskLevelText");
    const riskBadgeEl = document.getElementById("riskBadge");
    const riskCardEl = document.getElementById("riskCard");
    const gaugeProgress = document.getElementById("gaugeProgress");

    riskScoreEl.innerText = data.risk_score.toFixed(1);
    riskLevelTextEl.innerText = data.risk_level;
    riskBadgeEl.innerText = data.risk_badge;
    
    riskCardEl.className = "card glass-card risk-card"; 
    riskBadgeEl.className = "badge"; 
    
    let dangerColor = "var(--color-low)";
    if (data.risk_level === "EXTREME") {
        riskCardEl.classList.add("state-extreme");
        riskBadgeEl.classList.add("danger-extreme");
        dangerColor = "var(--color-extreme)";
    } else if (data.risk_level === "HIGH") {
        riskCardEl.classList.add("state-high");
        riskBadgeEl.classList.add("danger-high");
        dangerColor = "var(--color-high)";
    } else if (data.risk_level === "MODERATE") {
        riskCardEl.classList.add("state-moderate");
        riskBadgeEl.classList.add("danger-moderate");
        dangerColor = "var(--color-moderate)";
    } else {
        riskCardEl.classList.add("state-low");
        riskBadgeEl.classList.add("danger-low");
        dangerColor = "var(--color-low)";
    }

    const circumference = 314.16;
    const offset = circumference - (data.risk_score / 10.0) * circumference;
    gaugeProgress.style.stroke = dangerColor;
    gaugeProgress.style.strokeDashoffset = offset;

    document.getElementById("valPrecipSum").innerHTML = `${data.metrics.total_precip_7d.toFixed(1)} <span class="unit">mm</span>`;
    document.getElementById("valPrecipPeak").innerText = `Peak Rate: ${data.metrics.max_hourly_precip.toFixed(1)} mm/h`;
    document.getElementById("valConsecutiveRain").innerText = `Wet Days: ${data.metrics.consecutive_rain_days}d`;
    
    if (data.metrics.start_discharge !== null) {
        document.getElementById("valDischargePeak").innerHTML = `${data.metrics.peak_discharge.toFixed(1)} <span class="unit">m³/s</span>`;
        document.getElementById("valDischargeStart").innerText = `Baseline Start: ${data.metrics.start_discharge.toFixed(1)} m³/s`;
        document.getElementById("valDischargeSurge").innerText = `Surge Ratio: ${data.metrics.discharge_multiplier.toFixed(2)}x`;
    } else {
        document.getElementById("valDischargePeak").innerHTML = `N/A`;
        document.getElementById("valDischargeStart").innerText = `No river channels nearby`;
        document.getElementById("valDischargeSurge").innerText = `Surge Ratio: N/A`;
    }

    document.getElementById("valWeatherDesc").innerText = data.climate.weather_description;
    document.getElementById("valWindSpeed").innerText = `${data.climate.max_wind_speed} km/h`;
    document.getElementById("valHumidity").innerText = `${data.climate.humidity}%`;
    document.getElementById("valPressure").innerText = `${data.climate.surface_pressure} hPa`;
    document.getElementById("valUV").innerText = `${data.climate.max_uv_index}`;

    const reportContentEl = document.getElementById("reportContent");
    if (typeof marked !== 'undefined') {
        reportContentEl.innerHTML = marked.parse(data.summary_markdown);
    } else {
        reportContentEl.innerHTML = `<pre style="white-space: pre-wrap; font-family: var(--font-sans);">${data.summary_markdown}</pre>`;
    }

    const lat = data.location.latitude;
    const lon = data.location.longitude;
    map.setView([lat, lon], 12);
    
    if (hazardCircle) {
        map.removeLayer(hazardCircle);
    }
    
    let circleRadius = 1500 + (data.metrics.total_precip_7d * 40);
    if (circleRadius > 10000) circleRadius = 10000;
    
    hazardCircle = L.circle([lat, lon], {
        color: dangerColor,
        fillColor: dangerColor,
        fillOpacity: 0.22,
        weight: 2,
        radius: circleRadius
    }).addTo(map);
    
    hazardCircle.bindPopup(`<strong>Hazard Zone Center</strong><br>Level: ${data.risk_level}<br>Risk Score: ${data.risk_score}/10`).openPopup();

    updateTrendChart(data.visuals);
}

// 10. Update Chart Series
function updateTrendChart(visuals) {
    if (!trendChart) return;
    
    const parsedLabels = visuals.dates.map(dateStr => {
        try {
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
        } catch (e) {
            return dateStr;
        }
    });

    const sanitisedDischarge = visuals.river_discharge.map(v => v === null ? 0.0 : v);

    trendChart.data.labels = parsedLabels;
    trendChart.data.datasets[0].data = visuals.precipitation;
    trendChart.data.datasets[1].data = sanitisedDischarge;
    trendChart.update();
}
