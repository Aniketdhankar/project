// static/js/locationSearch.js

function initAutocomplete(inputId, callback) {
    const input = document.getElementById(inputId);
    if (!input) return;

    const autocomplete = new google.maps.places.Autocomplete(input, {
        componentRestrictions: { country: "IN" },
        types: ["geocode"]
    });

    autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();
        if (!place.geometry) return;
        
        callback({
            address: place.formatted_address,
            lat: place.geometry.location.lat(),
            lng: place.geometry.location.lng()
        });
    });
}

// Ensure Google Maps API script loads dynamically
function loadGoogleMaps(apiKey, callback) {
    if (window.google && window.google.maps) {
        callback();
        return;
    }

    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places`;
    script.async = true;
    script.onload = callback;
    document.head.appendChild(script);
}

// Export functions
export { initAutocomplete, loadGoogleMaps };
