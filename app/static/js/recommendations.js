/**
 * EduVerse AI - Recommendations Controller
 * Communicates with POST /api/recommend
 */

document.addEventListener('DOMContentLoaded', () => {
    initBudgetSlider();
    initRecommendForm();
});

function initBudgetSlider() {
    const slider = document.getElementById('pref-budget');
    const display = document.getElementById('budget-val-display');

    if (slider && display) {
        slider.addEventListener('input', (e) => {
            const val = parseInt(e.target.value);
            display.textContent = `₹${val.toLocaleString('en-IN')}`;
        });
    }
}

function initRecommendForm() {
    const form = document.getElementById('recommend-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const course = document.getElementById('pref-course')?.value;
        const district = document.getElementById('pref-district')?.value;
        const city = document.getElementById('pref-city')?.value.trim();
        const budget = parseFloat(document.getElementById('pref-budget')?.value || 100000);
        const college_type = document.getElementById('pref-type')?.value;
        const autonomous = document.getElementById('pref-autonomous')?.value;

        const facilities = Array.from(document.querySelectorAll('input[name="pref_facility"]:checked')).map(cb => cb.value);

        const payload = {
            course: course,
            state: "Tamil Nadu",
            district: district,
            city: city,
            budget: budget,
            college_type: college_type,
            autonomous: autonomous,
            facilities: facilities
        };

        const initial = document.getElementById('recommend-initial');
        const loading = document.getElementById('recommend-loading');
        const resultsContainer = document.getElementById('recommend-results');

        if (initial) initial.classList.add('hidden');
        if (loading) loading.classList.remove('hidden');
        if (resultsContainer) resultsContainer.classList.add('hidden');

        try {
            const res = await fetch('/api/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                const msg = errData?.error?.message || `Server returned error (${res.status})`;
                throw new Error(msg);
            }

            const data = await res.json();
            loading.classList.add('hidden');

            if (!data.success || !data.recommendations || data.recommendations.length === 0) {
                resultsContainer.classList.remove('hidden');
                resultsContainer.innerHTML = `
                    <div class="p-8 bg-white rounded-3xl border border-slate-200 text-center space-y-3">
                        <div class="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                        </div>
                        <h3 class="text-base font-bold text-slate-800">${data.message ? "District Information Notice" : "No Recommended Colleges Found"}</h3>
                        <p class="text-xs text-slate-600 max-w-sm mx-auto font-medium">
                            ${data.message || "None of the cataloged institutions matched your program or budget criteria. Try selecting another course or expanding your target district."}
                        </p>
                    </div>
                `;
                return;
            }

            renderRecommendations(data.recommendations, resultsContainer);
            resultsContainer.classList.remove('hidden');

        } catch (err) {
            console.error('Recommendation fetch error:', err);
            loading.classList.add('hidden');
            const userMsg = (err.message && !err.message.includes('fetch') && !err.message.includes('NetworkError'))
                ? err.message
                : 'Unable to connect to server. Please verify that the Flask server (python run.py) is running in your terminal.';
            showToast(userMsg, 'error');
        }
    });
}

function renderRecommendations(colleges, container) {
    container.innerHTML = `
        <div class="flex items-center justify-between pb-2">
            <h2 class="text-sm font-bold uppercase tracking-wider text-slate-700">Ranked Preference Matches</h2>
            <span class="text-xs font-semibold px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200 shadow-2xs">
                ${colleges.length} Matches Identified
            </span>
        </div>
    ` + colleges.map((c, index) => {
        const safeName = c.college_name.replace(/'/g, "\\'");
        const scoreColor = c.score >= 80 ? 'text-teal-700 bg-teal-50 border-teal-200' :
                           c.score >= 60 ? 'text-blue-700 bg-blue-50 border-blue-200' :
                           'text-amber-700 bg-amber-50 border-amber-200';

        const factorsHtml = (c.matching_factors || []).map(f => {
            const isWarning = f.startsWith('△') || f.startsWith('⚠️');
            const isInfo = f.startsWith('ℹ');
            const textClass = isWarning ? 'text-amber-700' : isInfo ? 'text-slate-500' : 'text-teal-700';
            return `<li class="text-xs ${textClass} flex items-start space-x-1.5 leading-snug"><span>${f}</span></li>`;
        }).join('');

        const feeFormatted = c.fee ? `₹${c.fee.toLocaleString('en-IN')} / yr` : 'Fee not available';

        return `
            <div class="p-6 bg-white rounded-3xl border border-slate-200 shadow-2xs hover:shadow-md hover:border-blue-200 transition space-y-4">
                <!-- Top Row: Rank, Name, Score -->
                <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                    <div class="flex items-start space-x-3">
                        <span class="w-7 h-7 rounded-xl bg-blue-900 text-white flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                            #${index + 1}
                        </span>
                        <div>
                            <div class="flex items-center space-x-2 flex-wrap">
                                <span class="text-[10px] font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200/60">
                                    ${c.college_type}
                                </span>
                                ${(c.is_autonomous || c.autonomous_status === 'AUTONOMOUS') ? `
                                    <span class="text-[10px] font-semibold px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200">
                                        Autonomous
                                    </span>
                                ` : ''}
                                <span class="text-[10px] text-slate-400 font-medium">
                                    ${c.data_status}
                                </span>
                            </div>
                            <h3 class="text-base font-bold text-slate-900 mt-1">
                                <a href="/college/${c.college_id}" class="hover:text-blue-600 transition">
                                    ${c.college_name}
                                </a>
                            </h3>
                            <p class="text-xs text-slate-500 mt-0.5">${c.location}</p>
                        </div>
                    </div>

                    <!-- Match Score Pill -->
                    <div class="flex sm:flex-col items-end justify-between sm:justify-start gap-1">
                        <span class="px-3 py-1.5 rounded-xl border text-sm font-extrabold ${scoreColor}">
                            ${c.score}% Match
                        </span>
                        <span class="text-[10px] text-slate-400 font-medium hidden sm:inline">Preference Fit</span>
                    </div>
                </div>

                <!-- Match Breakdown Checklist -->
                <div class="p-4 rounded-2xl bg-slate-50/70 border border-slate-200 space-y-2">
                    <div class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Why this college matched:</div>
                    <ul class="space-y-1.5">
                        ${factorsHtml}
                    </ul>
                </div>

                <!-- Footer Stats & Actions -->
                <div class="pt-2 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                    <div class="text-xs text-slate-600">
                        <span class="font-semibold text-slate-500">Starting Tuition:</span>
                        <span class="font-bold text-slate-900 ml-1">${feeFormatted}</span>
                    </div>

                    <div class="flex items-center space-x-2">
                        ${(c.official_website || c.official_website_url) ? `
                            <a href="${c.official_website || c.official_website_url}" target="_blank" rel="noopener noreferrer"
                               class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 transition flex items-center space-x-1 shadow-2xs">
                                <span>Visit Official Website</span>
                                <svg class="w-3.5 h-3.5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                            </a>
                        ` : ''}
                        <button type="button"
                                onclick="toggleCompare(${c.college_id})"
                                class="px-3 py-1.5 rounded-lg text-xs font-semibold border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 shadow-2xs transition cursor-pointer">
                            + Compare
                        </button>
                        <a href="/college/${c.college_id}" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 text-white hover:bg-blue-700 shadow-2xs transition">
                            View Profile &rarr;
                        </a>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}
