// static/js/ambulanceService.js

// Dummy ambulance data
const DUMMY_AMBULANCES = [
    { id: 1, type: "Basic Life Support", vehicleNumber: "DL01AB1234", driverName: "Rajesh Kumar", distance: "1.5", eta: "5 mins", rating: 4.8 },
    { id: 2, type: "Advanced Life Support", vehicleNumber: "DL02CD5678", driverName: "Amit Singh", distance: "2.3", eta: "8 mins", rating: 4.9 },
    { id: 3, type: "Patient Transport", vehicleNumber: "DL03EF9012", driverName: "Priya Sharma", distance: "3.0", eta: "12 mins", rating: 4.7 }
];

// Function to simulate finding nearby ambulances (sort by distance)
function findNearbyAmbulances(userLocation) {
    return new Promise((resolve) => {
        setTimeout(() => {
            const sortedAmbulances = DUMMY_AMBULANCES.map(ambulance => ({
                ...ambulance,
                distance: (Math.random() * 5).toFixed(1),
                eta: `${Math.floor(Math.random() * 10) + 5} mins`
            })).sort((a, b) => parseFloat(a.distance) - parseFloat(b.distance));

            resolve(sortedAmbulances);
        }, 1000); // Simulate network delay
    });
}

// Utility function to calculate distance between two lat/lng points
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth radius in km
    const dLat = deg2rad(lat2 - lat1);
    const dLon = deg2rad(lon2 - lon1);
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + 
              Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    return R * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))); // Distance in km
}

// Convert degrees to radians
function deg2rad(deg) {
    return deg * (Math.PI / 180);
}

// Export functions for use in other files
export { findNearbyAmbulances, calculateDistance };
