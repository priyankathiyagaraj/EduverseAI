/**
 * EduVerse AI - Comparison Controller
 */

async function removeComparison(collegeId) {
    try {
        const res = await fetch(`/api/compare/${collegeId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        });
        const data = await res.json();
        if (data.success) {
            location.reload();
        } else {
            showToast(data.error ? data.error.message : 'Failed to remove from matrix', 'error');
        }
    } catch (err) {
        console.error(err);
        showToast('Network error while removing college', 'error');
    }
}

async function clearComparison() {
    try {
        const res = await fetch('/api/compare/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        });
        const data = await res.json();
        if (data.success) {
            location.reload();
        }
    } catch (err) {
        console.error(err);
        showToast('Network error while clearing matrix', 'error');
    }
}
