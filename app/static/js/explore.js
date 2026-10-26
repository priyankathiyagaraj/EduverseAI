/**
 * EduVerse AI - College Explorer Frontend Controller
 * Connects frontend filters to backend SQLAlchemy endpoints via /api/colleges
 */

let currentPage = 1;
let mapInstance = null;
let mapMarkersGroup = null;
let searchTimeout = null;

document.addEventListener('DOMContentLoaded', () => {
    initFilters();
    initMobileFilters();
    initMapToggle();
    fetchColleges(1);
});

function toggleMobileFilters() {
    const container = document.getElementById('filter-sidebar-container');
    const chevron = document.getElementById('filter-chevron');
    if (!container) return;
    const isHidden = container.classList.contains('hidden');
    if (isHidden) {
        container.classList.remove('hidden');
        if (chevron) chevron.classList.add('rotate-180');
    } else {
        container.classList.add('hidden');
        if (chevron) chevron.classList.remove('rotate-180');
    }
}

function initMobileFilters() {
    const toggleBtn = document.getElementById('mobile-filter-toggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleMobileFilters);
    }
}

function initFilters() {
    const queryInput = document.getElementById('filter-query');
    const courseSelect = document.getElementById('filter-course');
    const districtSelect = document.getElementById('filter-district');
    const typeSelect = document.getElementById('filter-type');
    const autonomousSelect = document.getElementById('filter-autonomous');
    const feeInput = document.getElementById('filter-fee');
    const feeDisplay = document.getElementById('fee-display');
    const sortSelect = document.getElementById('filter-sort');
    const facilityCheckboxes = document.querySelectorAll('input[name="facility_checkbox"]');

    // Debounced text input
    if (queryInput) {
        queryInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                fetchColleges(1);
            }, 300);
        });
    }

    if (courseSelect) courseSelect.addEventListener('change', () => fetchColleges(1));
    if (districtSelect) districtSelect.addEventListener('change', () => fetchColleges(1));
    if (typeSelect) typeSelect.addEventListener('change', () => fetchColleges(1));
    if (autonomousSelect) autonomousSelect.addEventListener('change', () => fetchColleges(1));
    if (sortSelect) sortSelect.addEventListener('change', () => fetchColleges(1));

    if (feeInput && feeDisplay) {
        feeInput.addEventListener('input', (e) => {
            const val = parseInt(e.target.value);
            if (val >= 250000) {
                feeDisplay.textContent = 'Any Fee';
            } else {
                feeDisplay.textContent = `Up to ₹${val.toLocaleString('en-IN')}`;
            }
        });
        feeInput.addEventListener('change', () => fetchColleges(1));
    }

    facilityCheckboxes.forEach(cb => {
        cb.addEventListener('change', () => fetchColleges(1));
    });
}

function resetFilters() {
    const queryInput = document.getElementById('filter-query');
    const courseSelect = document.getElementById('filter-course');
    const districtSelect = document.getElementById('filter-district');
    const typeSelect = document.getElementById('filter-type');
    const autonomousSelect = document.getElementById('filter-autonomous');
    const feeInput = document.getElementById('filter-fee');
    const feeDisplay = document.getElementById('fee-display');
    const sortSelect = document.getElementById('filter-sort');
    const facilityCheckboxes = document.querySelectorAll('input[name="facility_checkbox"]');

    if (queryInput) queryInput.value = '';
    if (courseSelect) courseSelect.value = '';
    if (districtSelect) districtSelect.value = '';
    if (typeSelect) typeSelect.value = '';
    if (autonomousSelect) autonomousSelect.value = '';
    if (sortSelect) sortSelect.value = 'name';
    if (feeInput) feeInput.value = 250000;
    if (feeDisplay) feeDisplay.textContent = 'Any Fee';
    facilityCheckboxes.forEach(cb => cb.checked = false);

    fetchColleges(1);
}

async function fetchColleges(page = 1) {
    currentPage = page;
    const grid = document.getElementById('colleges-grid');
    const loading = document.getElementById('colleges-loading');
    const empty = document.getElementById('colleges-empty');
    const resultsCount = document.getElementById('results-count');

    grid.innerHTML = '';
    empty.classList.add('hidden');
    loading.classList.remove('hidden');
    resultsCount.textContent = 'Updating...';

    // Construct URL query params
    const params = new URLSearchParams();
    params.set('page', page);
    params.set('per_page', 9);

    const query = document.getElementById('filter-query')?.value.trim();
    if (query) params.set('query', query);

    const course = document.getElementById('filter-course')?.value;
    if (course) params.set('course', course);

    const district = document.getElementById('filter-district')?.value;
    if (district) params.set('district', district);

    const type = document.getElementById('filter-type')?.value;
    if (type) params.set('college_type', type);

    const autonomous = document.getElementById('filter-autonomous')?.value;
    if (autonomous) params.set('autonomous', autonomous);

    const feeVal = parseInt(document.getElementById('filter-fee')?.value || 250000);
    if (feeVal < 250000) params.set('max_fee', feeVal);

    const sort = document.getElementById('filter-sort')?.value;
    if (sort) params.set('sort', sort);

    const selectedFacilities = Array.from(document.querySelectorAll('input[name="facility_checkbox"]:checked')).map(cb => cb.value);
    selectedFacilities.forEach(f => params.append('facilities', f));

    try {
        const response = await fetch(`/api/colleges?${params.toString()}`);
        const data = await response.json();

        loading.classList.add('hidden');

        // Dynamic label: e.g. "52 MCA Colleges in Chennai Found"
        const courseVal = document.getElementById('filter-course')?.value;
        const districtVal = document.getElementById('filter-district')?.value;
        const typeVal = document.getElementById('filter-type')?.value;

        let labelParts = [];
        if (typeVal) labelParts.push(typeVal);
        if (courseVal) labelParts.push(courseVal);
        labelParts.push('Colleges');
        if (districtVal) labelParts.push(`in ${districtVal}`);
        else labelParts.push('in Tamil Nadu');

        if (!data.success || !data.colleges || data.colleges.length === 0) {
            empty.classList.remove('hidden');
            const emptyTitle = empty.querySelector('h3');
            const emptyDesc = empty.querySelector('p');
            if (districtVal) {
                if (emptyTitle) emptyTitle.textContent = "No colleges found matching criteria.";
                if (emptyDesc) emptyDesc.textContent = `No institutions matching your selected criteria were found in ${districtVal}. Try choosing 'All Courses' or relaxing filters.`;
            } else {
                if (emptyTitle) emptyTitle.textContent = "No Colleges Found";
                if (emptyDesc) emptyDesc.textContent = "We could not find any institutions matching your selected filter criteria. Try relaxing your budget ceiling or selecting another district.";
            }
            resultsCount.textContent = `0 ${labelParts.join(' ')} Found`;
            renderPagination({ total: 0, page: 1, total_pages: 1 });
            updateMapMarkers([]);
            return;
        }

        resultsCount.textContent = `${data.pagination.total} ${labelParts.join(' ')} Found`;

        renderColleges(data.colleges);
        renderPagination(data.pagination);
        updateMapMarkers(data.colleges);
        updateSaveButtonsState();

    } catch (err) {
        console.error('Fetch colleges failed:', err);
        loading.classList.add('hidden');
        resultsCount.textContent = 'Error loading colleges';
        showToast('Unable to connect to database. Check network or server status.', 'error');
    }
}

function renderColleges(colleges) {
    const grid = document.getElementById('colleges-grid');
    grid.innerHTML = colleges.map(col => {
        // Data status badge markup
        let statusBadge = '';
        if (col.data_status === 'VERIFIED') {
            statusBadge = `<span class="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                <svg class="w-3 h-3 mr-1 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path></svg>
                VERIFIED
            </span>`;
        } else if (col.data_status === 'SAMPLE') {
            statusBadge = `<span class="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-bold bg-amber-50 text-amber-700 border border-amber-200" title="Academic development sample data">
                SAMPLE DATA
            </span>`;
        } else if (col.data_status === 'ESTIMATED') {
            statusBadge = `<span class="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-bold bg-sky-50 text-sky-700 border border-sky-200">
                ESTIMATED
            </span>`;
        } else {
            statusBadge = `<span class="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-bold bg-slate-100 text-slate-600 border border-slate-200">
                NOT AVAILABLE
            </span>`;
        }

        // Fee display
        let feeDisplay = '<span class="text-xs text-slate-400 italic">Information not available</span>';
        if (col.min_fee !== null && col.min_fee !== undefined) {
            const minFormatted = col.min_fee.toLocaleString('en-IN');
            if (col.max_fee && col.max_fee > col.min_fee) {
                feeDisplay = `<span class="text-sm font-bold text-slate-900">₹${minFormatted} <span class="text-xs font-normal text-slate-500">- ₹${col.max_fee.toLocaleString('en-IN')}</span></span>`;
            } else {
                feeDisplay = `<span class="text-sm font-bold text-slate-900">₹${minFormatted}</span>`;
            }
        }

        // Courses chips
        const coursesSlice = col.courses ? col.courses.slice(0, 3) : [];
        const coursesHtml = coursesSlice.map(c => `
            <span class="inline-block px-2 py-0.5 rounded-md text-[11px] bg-slate-100 text-slate-700 font-medium">
                ${c.course_name}
            </span>
        `).join('');
        const extraCourses = (col.courses && col.courses.length > 3) ? `
            <span class="inline-block px-1.5 py-0.5 rounded-md text-[11px] bg-slate-50 text-slate-400">
                +${col.courses.length - 3} more
            </span>
        ` : '';

        // Facilities chips
        const facilitiesSlice = col.facilities ? col.facilities.slice(0, 3) : [];
        const facilitiesHtml = facilitiesSlice.map(f => `
            <span class="text-[10px] text-slate-500 bg-slate-50 border border-slate-100 rounded px-1.5 py-0.5">
                ✓ ${f}
            </span>
        `).join('');

        const safeName = col.name.replace(/'/g, "\\'");
        const safeCity = (col.city || '').replace(/'/g, "\\'");
        const directionsUrl = col.directions_url || `https://www.google.com/maps/dir/?api=1&destination=${col.latitude},${col.longitude}`;

        return `
            <div class="h-full bg-white rounded-2xl border border-slate-200 shadow-2xs hover:shadow-md hover:border-blue-200 transition-all duration-200 flex flex-col justify-between overflow-hidden group">
                <div class="p-6 flex-1 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between gap-2 mb-3">
                            <div class="flex items-center gap-1.5 flex-wrap">
                                <span class="inline-block px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200/60">
                                    ${col.college_type}
                                </span>
                                ${(col.is_autonomous || col.autonomous_status === 'AUTONOMOUS') ? `
                                    <span class="inline-block px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">
                                        Autonomous
                                    </span>
                                ` : ''}
                            </div>
                            ${statusBadge}
                        </div>

                        <h3 class="text-base font-bold text-slate-900 group-hover:text-blue-600 transition tracking-tight line-clamp-2 leading-snug">
                            <a href="/college/${col.id}">${col.name}</a>
                        </h3>

                        <div class="flex items-center justify-between text-xs text-slate-500 mt-2">
                            <div class="flex items-center space-x-1.5">
                                <svg class="w-3.5 h-3.5 text-slate-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                </svg>
                                <span class="font-medium text-slate-600">${col.city}, ${col.district}</span>
                            </div>
                            <span class="text-amber-600 font-bold">★ ${col.rating || 4.2}</span>
                        </div>

                        <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                            <span class="text-xs text-slate-400 font-medium">Annual Tuition:</span>
                            ${feeDisplay}
                        </div>

                        <div class="mt-3">
                            <div class="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5">Courses Offered:</div>
                            <div class="flex flex-wrap gap-1.5 min-h-[26px]">
                                ${coursesHtml}
                                ${extraCourses}
                            </div>
                        </div>

                        <div class="mt-3 flex flex-wrap gap-1">
                            ${facilitiesHtml}
                        </div>

                        <!-- Campus Map & Directions Actions -->
                        <div class="mt-4 pt-3 border-t border-slate-100 grid grid-cols-2 gap-2">
                            <button type="button"
                                    onclick="focusCollegeOnMap(${col.latitude}, ${col.longitude}, '${safeName}', '${safeCity}', ${col.id})"
                                    class="px-2.5 py-1.5 rounded-xl text-xs font-semibold bg-blue-50 text-blue-700 hover:bg-blue-100 transition flex items-center justify-center gap-1.5 cursor-pointer">
                                <svg class="w-3.5 h-3.5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path>
                                </svg>
                                <span>Campus Map</span>
                            </button>
                            <a href="${directionsUrl}" target="_blank" rel="noopener noreferrer"
                               class="px-2.5 py-1.5 rounded-xl text-xs font-semibold bg-teal-50 text-teal-700 hover:bg-teal-100 transition flex items-center justify-center gap-1.5">
                                <svg class="w-3.5 h-3.5 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                </svg>
                                <span>Directions ↗</span>
                            </a>
                        </div>

                        <!-- Official Website Link / Availability -->
                        <div class="mt-2.5">
                            ${(col.official_website || col.official_website_url) ? `
                                <a href="${col.official_website || col.official_website_url}" target="_blank" rel="noopener noreferrer"
                                   class="w-full py-2 px-3 rounded-xl text-xs font-semibold bg-blue-50 hover:bg-blue-100 border border-blue-200 text-blue-700 transition flex items-center justify-center gap-1.5 group/btn shadow-2xs">
                                    <span>Visit Official Website</span>
                                    <svg class="w-3.5 h-3.5 text-blue-600 group-hover/btn:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                                </a>
                            ` : `
                                <div class="w-full py-1.5 px-3 rounded-xl text-[11px] font-medium bg-slate-50 border border-slate-200/80 text-slate-400 text-center flex items-center justify-center gap-1">
                                    <span>Official website not available</span>
                                </div>
                            `}
                        </div>
                    </div>
                </div>

                <div class="px-6 py-3.5 bg-slate-50/90 border-t border-slate-100 flex items-center justify-between gap-2">
                    <a href="/college/${col.id}" class="text-xs font-semibold text-blue-600 hover:text-blue-800 transition flex items-center space-x-1">
                        <span>View Profile</span>
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                    </a>
                    <div class="flex items-center space-x-2">
                        <button type="button"
                                data-save-college-id="${col.id}"
                                onclick="toggleSaveCollege(${col.id}, '${safeName}')"
                                class="px-2.5 py-1.5 rounded-lg text-xs font-semibold border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 shadow-2xs transition flex items-center space-x-1 cursor-pointer">
                            <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"></path></svg>
                            <span>Save</span>
                        </button>
                        <button type="button"
                                onclick="toggleCompare(${col.id}, '${safeName}')"
                                class="px-2.5 py-1.5 rounded-lg text-xs font-semibold border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:border-slate-300 shadow-2xs transition flex items-center space-x-1 cursor-pointer">
                            <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                            </svg>
                            <span>Compare</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function renderPagination(p) {
    const container = document.getElementById('pagination-container');
    if (!container) return;

    if (p.total <= p.per_page) {
        container.innerHTML = `<span class="text-xs text-slate-400">Showing all ${p.total} institutions</span>`;
        return;
    }

    let buttons = '';
    // Previous button
    buttons += `
        <button type="button"
                onclick="fetchColleges(${p.page - 1})"
                ${!p.has_prev ? 'disabled' : ''}
                class="px-3 py-1.5 rounded-lg text-xs font-medium border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed">
            &larr; Previous
        </button>
    `;

    // Page indicator
    buttons += `
        <span class="text-xs text-slate-600 font-medium">
            Page <span class="font-bold text-slate-900">${p.page}</span> of <span class="font-bold text-slate-900">${p.total_pages}</span>
        </span>
    `;

    // Next button
    buttons += `
        <button type="button"
                onclick="fetchColleges(${p.page + 1})"
                ${!p.has_next ? 'disabled' : ''}
                class="px-3 py-1.5 rounded-lg text-xs font-medium border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed">
            Next &rarr;
        </button>
    `;

    container.innerHTML = buttons;
}

// Leaflet Map Integration
function initMapToggle() {
    const toggleBtn = document.getElementById('toggle-map-btn');
    const mapWrapper = document.getElementById('map-wrapper');
    const toggleText = document.getElementById('toggle-map-text');

    if (!toggleBtn || !mapWrapper) return;

    toggleBtn.addEventListener('click', () => {
        const isHidden = mapWrapper.classList.contains('hidden');
        if (isHidden) {
            mapWrapper.classList.remove('hidden');
            toggleText.textContent = 'Hide Map View';
            ensureMapInitialized();
        } else {
            mapWrapper.classList.add('hidden');
            toggleText.textContent = 'Show Map View';
        }
    });
}

function ensureMapInitialized() {
    if (!mapInstance) {
        // Center on Tamil Nadu (lat: 11.1271, lng: 78.6569, zoom: 7)
        mapInstance = L.map('colleges-map').setView([11.1271, 78.6569], 7);

        // OpenStreetMap Tile Layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 18
        }).addTo(mapInstance);

        mapMarkersGroup = L.featureGroup().addTo(mapInstance);
    }
    setTimeout(() => mapInstance.invalidateSize(), 150);
}

function updateMapMarkers(colleges) {
    if (!mapInstance || !mapMarkersGroup) return;

    mapMarkersGroup.clearLayers();
    let hasMarkers = false;

    colleges.forEach(c => {
        if (c.latitude && c.longitude) {
            hasMarkers = true;
            const marker = L.marker([c.latitude, c.longitude]);
            const directionsUrl = c.directions_url || `https://www.google.com/maps/dir/?api=1&destination=${c.latitude},${c.longitude}`;
            marker.bindPopup(`
                <div class="p-1 space-y-1.5 min-w-[200px]">
                    <div class="flex items-center gap-1">
                        <span class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700">${c.college_type}</span>
                        ${(c.is_autonomous || c.autonomous_status === 'AUTONOMOUS') ? '<span class="text-[10px] font-semibold text-amber-600">Autonomous</span>' : ''}
                    </div>
                    <strong class="text-xs font-bold text-slate-900 block">${c.name}</strong>
                    <span class="text-[11px] text-slate-600 block">${c.city}, ${c.district}</span>
                    <div class="flex items-center justify-between pt-1 border-t border-slate-100">
                        <a href="/college/${c.id}" class="text-xs font-semibold text-indigo-600 hover:underline">
                            View Profile &rarr;
                        </a>
                        <a href="${directionsUrl}" target="_blank" rel="noopener noreferrer" class="text-xs font-semibold text-emerald-600 hover:underline">
                            Directions ↗
                        </a>
                    </div>
                </div>
            `);
            mapMarkersGroup.addLayer(marker);
        }
    });

    if (hasMarkers) {
        mapInstance.fitBounds(mapMarkersGroup.getBounds().pad(0.1));
    }
}

function focusCollegeOnMap(lat, lng, name, city, id) {
    const mapWrapper = document.getElementById('map-wrapper');
    const toggleText = document.getElementById('toggle-map-text');
    if (mapWrapper && mapWrapper.classList.contains('hidden')) {
        mapWrapper.classList.remove('hidden');
        if (toggleText) toggleText.textContent = 'Hide Map View';
    }
    ensureMapInitialized();
    if (mapWrapper) {
        mapWrapper.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    setTimeout(() => {
        if (mapInstance) {
            mapInstance.invalidateSize();
            mapInstance.setView([lat, lng], 15);
            const directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`;
            L.popup()
                .setLatLng([lat, lng])
                .setContent(`
                    <div class="p-1 space-y-1.5 min-w-[200px]">
                        <strong class="text-xs font-bold text-slate-900 block">${name}</strong>
                        <span class="text-[11px] text-slate-600 block">${city}</span>
                        <div class="flex items-center justify-between pt-1 border-t border-slate-100">
                            <a href="/college/${id}" class="text-xs font-semibold text-indigo-600 hover:underline">
                                View Profile &rarr;
                            </a>
                            <a href="${directionsUrl}" target="_blank" class="text-xs font-semibold text-emerald-600 hover:underline">
                                Directions ↗
                            </a>
                        </div>
                    </div>
                `)
                .openOn(mapInstance);
        }
    }, 250);
}

function toggleSaveCollege(id, name) {
    let saved = JSON.parse(localStorage.getItem('eduverse_saved_colleges') || '[]');
    const index = saved.findIndex(item => item.id === id);
    if (index > -1) {
        saved.splice(index, 1);
        localStorage.setItem('eduverse_saved_colleges', JSON.stringify(saved));
        showToast(`Removed "${name}" from saved list.`, 'info');
    } else {
        saved.push({ id, name, savedAt: new Date().toISOString() });
        localStorage.setItem('eduverse_saved_colleges', JSON.stringify(saved));
        showToast(`Saved "${name}" to your shortlist!`, 'success');
    }
    updateSaveButtonsState();
}

function updateSaveButtonsState() {
    let saved = JSON.parse(localStorage.getItem('eduverse_saved_colleges') || '[]');
    const savedIds = new Set(saved.map(item => item.id));
    document.querySelectorAll('[data-save-college-id]').forEach(btn => {
        const id = parseInt(btn.getAttribute('data-save-college-id'));
        if (savedIds.has(id)) {
            btn.classList.add('bg-amber-50', 'text-amber-700', 'border-amber-300');
            btn.classList.remove('bg-white', 'text-slate-700', 'border-slate-300');
            btn.innerHTML = `
                <svg class="w-3.5 h-3.5 text-amber-500 fill-current" viewBox="0 0 24 24"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
                <span>Saved</span>
            `;
        } else {
            btn.classList.remove('bg-amber-50', 'text-amber-700', 'border-amber-300');
            btn.classList.add('bg-white', 'text-slate-700', 'border-slate-300');
            btn.innerHTML = `
                <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"></path></svg>
                <span>Save</span>
            `;
        }
    });
}
