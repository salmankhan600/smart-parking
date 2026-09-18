/* ========================================================
   Park3D - Admin Dashboard Charts & Live Override Logic
   ======================================================== */

// Initialize Chart.js analytics graphs
function initAdminCharts(dailyStats, slotMetrics) {
    // 1. Daily Bookings Chart
    const bookingCtx = document.getElementById('bookingChart');
    if (bookingCtx) {
        const labels = dailyStats.map(d => d.date);
        const dataValues = dailyStats.map(d => d.bookings);

        new Chart(bookingCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Bookings',
                    data: dataValues,
                    borderColor: '#00f3ff',
                    backgroundColor: 'rgba(0, 243, 255, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
                }
            }
        });
    }

    // 2. Occupancy Breakdown Doughnut Chart
    const occupancyCtx = document.getElementById('occupancyChart');
    if (occupancyCtx && slotMetrics) {
        new Chart(occupancyCtx, {
            type: 'doughnut',
            data: {
                labels: ['Available', 'Occupied', 'Reserved', 'Disabled'],
                datasets: [{
                    data: [
                        slotMetrics.available_slots,
                        slotMetrics.occupied_slots,
                        slotMetrics.reserved_slots,
                        slotMetrics.disabled_slots
                    ],
                    backgroundColor: ['#00ff66', '#ff3366', '#ffb700', '#0088ff'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#f0f4f8' } }
                }
            }
        });
    }
}

// Trigger DEMO MODE Live Traffic Simulator
async function triggerDemoSimulation() {
    try {
        const res = await fetch('/api/admin/demo-simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await res.json();
        if (data.success) {
            showToast(`DEMO MODE: ${data.message}`, 'success');
            if (window.parkEngine) {
                window.parkEngine.loadFloorData();
            }
        } else {
            showToast(data.message, 'error');
        }
    } catch (err) {
        console.error("Demo simulation error:", err);
    }
}
