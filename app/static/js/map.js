/**
 * EduVerse AI - Tamil Nadu Campus Map Controller
 * Leaflet.js + OpenStreetMap integration with coordinate verification
 */

document.addEventListener('DOMContentLoaded', () => {
    const dataEl = document.getElementById('colleges-map-data');
    if (!dataEl) return;

    let colleges = [];
    try {
        colleges = JSON.parse(dataEl.textContent);
    } catch (e) {
        console.error('Failed to parse colleges map data', e);
        return;
    }

    initTamilNaduMap(colleges);
});

function initTamilNaduMap(colleges) {
    const mapContainer = document.getElementById('tn-leaflet-map');
    if (!mapContainer) return;

    // Center on Tamil Nadu geographical midpoint
    const map = L.map('tn-leaflet-map').setView([11.1271, 78.6569], 7);

    // OpenStreetMap standard tile layer with mandatory attribution
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18
    }).addTo(map);

    const markersGroup = L.featureGroup().addTo(map);
    const markersMap = new Map();

    function renderMarkersAndList(filteredColleges) {
        markersGroup.clearLayers();
        markersMap.clear();

        const listContainer = document.getElementById('map-college-list');
        const countBadge = document.getElementById('map-marker-count');
        if (listContainer) listContainer.innerHTML = '';

        if (!filteredColleges || filteredColleges.length === 0) {
            if (listContainer) {
                listContainer.innerHTML = `
                    <div class="p-6 text-center text-xs text-slate-500 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
                        <p class="font-bold text-slate-700">No Matching Campuses</p>
                        <p class="text-[11px] text-slate-400">Try changing your search term to find colleges in Tamil Nadu.</p>
                    </div>
                `;
            }
            if (countBadge) countBadge.textContent = '0 Campuses Mapped';
            return;
        }

        let validCount = 0;

        filteredColleges.forEach(col => {
            const hasCoords = col.latitude !== null && col.longitude !== null &&
                              col.latitude >= -90 && col.latitude <= 90 &&
                              col.longitude >= -180 && col.longitude <= 180;

            const card = document.createElement('div');
            card.className = 'p-3 rounded-xl border border-slate-200 bg-white hover:bg-indigo-50/60 hover:border-indigo-200 transition cursor-pointer space-y-1.5 shadow-xs';

            const directionsUrl = col.directions_url || `https://www.google.com/maps/dir/?api=1&destination=${col.latitude},${col.longitude}`;
            const coursesList = (col.courses && col.courses.length > 0)
                ? col.courses.slice(0, 3).map(c => `<span class="px-1.5 py-0.5 rounded text-[10px] bg-slate-100 text-slate-700">${c.course_name}</span>`).join(' ')
                : '';

            if (hasCoords) {
                validCount++;
                const marker = L.marker([col.latitude, col.longitude]);
                marker.bindPopup(`
                    <div class="p-1 space-y-1.5 min-w-[220px]">
                        <div class="flex items-center gap-1.5 flex-wrap">
                            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100">${col.college_type}</span>
                            ${(col.is_autonomous || col.autonomous_status === 'AUTONOMOUS') ? '<span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200">Autonomous</span>' : ''}
                        </div>
                        <h4 class="text-sm font-bold text-slate-900 leading-snug">${col.name}</h4>
                        <p class="text-xs text-slate-600 flex items-center gap-1">
                            <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path></svg>
                            ${col.city}, ${col.district}
                        </p>
                        ${coursesList ? `<div class="flex flex-wrap gap-1 pt-1">${coursesList}</div>` : ''}
                        <div class="flex items-center justify-between pt-2 border-t border-slate-100">
                            <a href="/college/${col.id}" class="text-xs font-semibold text-indigo-600 hover:text-indigo-800">
                                View Profile &rarr;
                            </a>
                            <a href="${directionsUrl}" target="_blank" rel="noopener noreferrer" class="text-xs font-semibold text-emerald-600 hover:text-emerald-800 flex items-center gap-0.5">
                                <span>Directions</span> ↗
                            </a>
                        </div>
                    </div>
                `);
                markersGroup.addLayer(marker);
                markersMap.set(col.id, marker);

                card.innerHTML = `
                    <div class="flex items-center justify-between">
                        <span class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700">${col.college_type}</span>
                        ${(col.is_autonomous || col.autonomous_status === 'AUTONOMOUS') ? '<span class="text-[10px] font-semibold text-amber-600">Autonomous</span>' : ''}
                    </div>
                    <h5 class="text-xs font-bold text-slate-900 line-clamp-1">${col.name}</h5>
                    <p class="text-[11px] text-slate-500">${col.city}, ${col.district}</p>
                    <div class="flex items-center justify-between pt-1 text-[11px]">
                        <span class="text-emerald-600 font-medium">✓ Verified Campus</span>
                        <a href="${directionsUrl}" target="_blank" rel="noopener noreferrer" class="text-indigo-600 hover:underline font-semibold" onclick="event.stopPropagation()">Directions ↗</a>
                    </div>
                `;

                card.addEventListener('click', () => {
                    map.setView([col.latitude, col.longitude], 14);
                    marker.openPopup();
                });
            }

            if (listContainer) listContainer.appendChild(card);
        });

        if (countBadge) {
            countBadge.textContent = `${validCount} Campuses Mapped`;
        }

        if (validCount > 0) {
            map.fitBounds(markersGroup.getBounds().pad(0.05));
        }
    }

    renderMarkersAndList(colleges);

    // Search filter input listener
    const searchInput = document.getElementById('map-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase().trim();
            const filtered = colleges.filter(c =>
                c.name.toLowerCase().includes(term) ||
                c.district.toLowerCase().includes(term) ||
                c.city.toLowerCase().includes(term)
            );
            renderMarkersAndList(filtered);
        });
    }
}
