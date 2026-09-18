/* ========================================================
   Park3D - Booking & Payment Handling + QR Pass Generator
   ======================================================== */

// Calculate Price Dynamically based on duration selection
function updateBookingPrice(pricePerHour) {
    const durationEl = document.getElementById('duration-select');
    const priceDisplay = document.getElementById('total-price-display');
    if (!durationEl || !priceDisplay) return;

    const hours = parseInt(durationEl.value || '1');
    let total = 0;

    if (hours === 1) total = pricePerHour;
    else if (hours === 2) total = pricePerHour * 1.8;
    else if (hours === 3) total = pricePerHour * 2.5;
    else if (hours === 4) total = pricePerHour * 3.2;
    else total = pricePerHour * (hours * 0.75);

    priceDisplay.innerText = `₹${total.toFixed(2)}`;
}

// Generate QR Code Parking Pass on confirmation page
function generateParkingQRCode(bookingCode, dataString) {
    const qrContainer = document.getElementById('qrcode-canvas');
    if (!qrContainer) return;

    qrContainer.innerHTML = '';
    new QRCode(qrContainer, {
        text: dataString || bookingCode,
        width: 180,
        height: 180,
        colorDark: "#00f3ff",
        colorLight: "#050811",
        correctLevel: QRCode.CorrectLevel.H
    });
}
