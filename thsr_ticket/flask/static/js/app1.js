document.addEventListener('DOMContentLoaded', function() {
    // JavaScript to populate the travel_date select element
    flatpickr("#travel_date", {
        minDate: "today",
        maxDate: new Date().fp_incr(30) // 30 days from now
    });
});