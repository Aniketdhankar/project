// Static arrays for direct booking
const users = [
    { id: "user1", name: "Swasti", location: { lat: 20.593, lng: 78.9615 } },
  ];
  
  let staticAmbulances = [
    {
      id: "amb1",
      driverId: "123",
      location: { lat: 20.5937, lng: 78.9629 },
      status: "available",
    },
    {
      id: "amb2",
      driverId: "456",
      location: { lat: 20.5945, lng: 78.965 },
      status: "available",
    },
  ];
  
  let booking = null;
  
  document.addEventListener("DOMContentLoaded", async function () {
      const root = document.getElementById("ambulance-booking-root");
      if (!root) return;
  
      // Insert both Direct Booking and Location-based Search sections
      root.innerHTML = `
          <div class="container mt-4">
              <h1 class="text-center mb-4">🚑 Emergency Ambulance Booking</h1>
              
              <!-- Direct Booking Section -->
              <div id="bookingFormSection" class="mb-4">
                  <div class="card">
                      <div class="card-body">
                          <h5 class="card-title">Book an Ambulance Directly</h5>
                          <button class="btn btn-primary w-100" id="confirmBooking">Confirm Booking</button>
                          <div id="bookingConfirmation" class="mt-2 text-success"></div>
                      </div>
                  </div>
              </div>
              
              <!-- Location-based Search Section -->
              <div id="locationSearchSection">
                  <div class="card">
                      <div class="card-body">
                          <h5 class="card-title">Enter Your Location</h5>
                          <input type="text" id="locationInput" class="form-control mb-2" placeholder="Enter your location">
                          <button class="btn btn-primary w-100" id="findAmbulances">Find Ambulances</button>
                      </div>
                  </div>
                  <div id="ambulanceList" class="mt-3"></div>
              </div>
          </div>
      `;
  
      // (Assuming initLocationSearch is defined in locationSearch.js)
      initLocationSearch();
  
      // Direct Booking: Attach event listener for "Confirm Booking" button
      document.getElementById("confirmBooking").addEventListener("click", function () {
          if (booking) {
              alert("Ambulance already booked!");
              return;
          }
          const user = users[0];
          const availableAmbulance = staticAmbulances.find(amb => amb.status === "available");
          if (!availableAmbulance) {
              alert("No ambulances available!");
              return;
          }
          // Create a new booking and mark the ambulance as booked
          booking = {
              userId: user.id,
              ambulanceId: availableAmbulance.id,
              status: "confirmed"
          };
          availableAmbulance.status = "booked";
          document.getElementById("bookingConfirmation").innerHTML = `🚑 Ambulance ${booking.ambulanceId} is on the way!`;
      });
  
      // Location-based Search: Attach event listener for "Find Ambulances" button
      document.getElementById("findAmbulances").addEventListener("click", async function () {
          const location = document.getElementById("locationInput").value;
          if (!location) {
              alert("Please enter your location!");
              return;
          }
          const ambulances = await findNearbyAmbulances(location);
          displayAmbulances(ambulances);
      });
  });
  
  // Function to display ambulances from location-based search
  function displayAmbulances(ambulances) {
      const listContainer = document.getElementById("ambulanceList");
      listContainer.innerHTML = "";
  
      if (ambulances.length === 0) {
          listContainer.innerHTML = `<div class="alert alert-warning">No ambulances found nearby.</div>`;
          return;
      }
  
      ambulances.forEach(amb => {
          const card = document.createElement("div");
          card.classList.add("card", "mb-3");
  
          card.innerHTML = `
              <div class="card-body">
                  <h5 class="card-title">${amb.type} - ${amb.vehicleNumber}</h5>
                  <p class="card-text">
                      <strong>Driver:</strong> ${amb.driverName} <br>
                      <strong>Distance:</strong> ${amb.distance} km <br>
                      <strong>ETA:</strong> ${amb.eta} mins <br>
                      <strong>Rating:</strong> ⭐ ${amb.rating}
                  </p>
                  <button class="btn btn-success w-100 book-ambulance" data-id="${amb.id}">Book Ambulance</button>
              </div>
          `;
  
          listContainer.appendChild(card);
      });
  
      // Attach event listeners to each "Book Ambulance" button in the list
      document.querySelectorAll(".book-ambulance").forEach(button => {
          button.addEventListener("click", function () {
              const ambulanceId = this.getAttribute("data-id");
              alert(`Ambulance ${ambulanceId} booked! 🚑`);
          });
      });
  }
  