/**
 * EduVerse AI - Analytics Controller
 * Renders 4 Chart.js visualizations driven by live database queries
 */

document.addEventListener('DOMContentLoaded', () => {
    const dataElement = document.getElementById('analytics-data');
    if (!dataElement) return;

    let data;
    try {
        data = JSON.parse(dataElement.textContent);
    } catch (e) {
        console.error('Failed to parse analytics JSON:', e);
        return;
    }

    renderDistrictChart(data.colleges_by_district);
    renderTypeChart(data.ownership_distribution || data.colleges_by_type);
    renderAutonomousChart(data.autonomous_distribution);
    renderCityChart(data.colleges_by_city);
    renderFeeChart(data.fee_distribution);
    renderCourseChart(data.courses_availability);
});

// Chart 1: Colleges by District (All 38 Tamil Nadu Districts)
function renderDistrictChart(districtData) {
    const ctx = document.getElementById('districtChart');
    if (!ctx || !districtData) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: districtData.labels,
            datasets: [{
                label: 'Colleges',
                data: districtData.counts,
                backgroundColor: districtData.counts.map(c => c > 0 ? 'rgba(79, 70, 229, 0.85)' : 'rgba(203, 213, 225, 0.5)'),
                borderColor: districtData.counts.map(c => c > 0 ? 'rgb(79, 70, 229)' : 'rgb(148, 163, 184)'),
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const val = context.raw;
                            if (val === 0) {
                                return ' 0 colleges currently available in EduVerse database';
                            }
                            return ` ${val} college${val > 1 ? 's' : ''} cataloged`;
                        },
                        afterLabel: function(context) {
                            const val = context.raw;
                            if (val === 0) {
                                return ' (District recognized; awaiting college data ingestion)';
                            }
                            return null;
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        autoSkip: false,
                        maxRotation: 90,
                        minRotation: 45,
                        font: { size: 9 }
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0 }
                }
            }
        }
    });
}

// Chart 2: College Distribution by Type
function renderTypeChart(typeData) {
    const ctx = document.getElementById('typeChart');
    if (!ctx || !typeData) return;

    const palette = [
        '#4f46e5', // Indigo
        '#059669', // Emerald
        '#d97706', // Amber
        '#0284c7', // Sky
        '#7c3aed', // Purple
        '#e11d48'  // Rose
    ];

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: typeData.labels,
            datasets: [{
                data: typeData.counts,
                backgroundColor: palette.slice(0, typeData.labels.length),
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        padding: 12,
                        font: { size: 11 }
                    }
                }
            }
        }
    });
}

// Chart 3: Annual Tuition Fee Brackets
function renderFeeChart(feeData) {
    const ctx = document.getElementById('feeChart');
    if (!ctx || !feeData) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: feeData.labels,
            datasets: [{
                label: 'Offered Courses',
                data: feeData.counts,
                backgroundColor: [
                    'rgba(5, 150, 105, 0.85)',  // Emerald
                    'rgba(14, 165, 233, 0.85)',  // Sky
                    'rgba(79, 70, 229, 0.85)',  // Indigo
                    'rgba(217, 119, 6, 0.85)',  // Amber
                    'rgba(225, 29, 72, 0.85)',  // Rose
                    'rgba(100, 116, 139, 0.85)' // Slate
                ],
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0 }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 20,
                        font: { size: 10 }
                    }
                }
            }
        }
    });
}

// Chart 6: Top Courses Availability
function renderCourseChart(courseData) {
    const ctx = document.getElementById('courseChart');
    if (!ctx || !courseData) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: courseData.labels,
            datasets: [{
                label: 'Institutions Offering Course',
                data: courseData.counts,
                backgroundColor: 'rgba(99, 102, 241, 0.85)',
                borderColor: 'rgb(79, 70, 229)',
                borderWidth: 1,
                borderRadius: 8
            }]
        },
        options: {
            indexAxis: 'y', // Horizontal bars
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { precision: 0 }
                }
            }
        }
    });
}

// Chart 3: Autonomous vs Non-Autonomous
function renderAutonomousChart(autoData) {
    const ctx = document.getElementById('autonomousChart');
    if (!ctx || !autoData) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: autoData.labels,
            datasets: [{
                data: autoData.counts,
                backgroundColor: ['#9333ea', '#94a3b8'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        padding: 12,
                        font: { size: 11 }
                    }
                }
            }
        }
    });
}

// Chart 4: Colleges by City (Top 10)
function renderCityChart(cityData) {
    const ctx = document.getElementById('cityChart');
    if (!ctx || !cityData) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: cityData.labels,
            datasets: [{
                label: 'Colleges in City',
                data: cityData.counts,
                backgroundColor: 'rgba(2, 132, 199, 0.85)',
                borderColor: 'rgb(2, 132, 199)',
                borderWidth: 1,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 20,
                        font: { size: 10 }
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0 }
                }
            }
        }
    });
}
