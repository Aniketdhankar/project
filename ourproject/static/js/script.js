document.addEventListener("DOMContentLoaded", function () {
    fetchDonors();

    document.getElementById("donorForm").addEventListener("submit", async function (e) {
        e.preventDefault();

        const donorData = {
            name: document.getElementById("name").value,
            age: document.getElementById("age").value,
            blood_type: document.getElementById("bloodType").value,
            organs: document.getElementById("organs").value,
            contact: document.getElementById("contact").value,
            location: document.getElementById("location").value,
            hla: document.getElementById("hla").value
        };

        const response = await fetch("/api/donors", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(donorData)
        });

        if (response.ok) {
            alert("Donor registered successfully!");
            fetchDonors();
            document.getElementById("donorForm").reset();
        }
    });
});

async function fetchDonors() {
    const response = await fetch("/api/donors");
    const donors = await response.json();
    const donorTable = document.getElementById("donorTable");
    donorTable.innerHTML = "";

    donors.forEach(donor => {
        const row = `<tr>
            <td>${donor.name}</td>
            <td>${donor.age}</td>
            <td>${donor.blood_type}</td>
            <td>${donor.organs}</td>
            <td>${donor.contact}</td>
            <td>${donor.location}</td>
            <td>${donor.hla}</td>
        </tr>`;
        donorTable.innerHTML += row;
    });
}

async function searchDonors() {
    const location = document.getElementById("searchLocation").value;
    const hla = document.getElementById("searchHLA").value;

    const response = await fetch(`/api/search?location=${location}&hla=${hla}`);
    const searchResults = await response.json();
    const searchTable = document.getElementById("searchResults");
    searchTable.innerHTML = "";

    if (searchResults.length === 0) {
        alert("No compatible donors found.");
    }

    searchResults.forEach(donor => {
        const row = `<tr>
            <td>${donor.name}</td>
            <td>${donor.age}</td>
            <td>${donor.blood_type}</td>
            <td>${donor.organs}</td>
            <td>${donor.contact}</td>
            <td>${donor.location}</td>
            <td>${donor.hla}</td>
        </tr>`;
        searchTable.innerHTML += row;
    });
}
