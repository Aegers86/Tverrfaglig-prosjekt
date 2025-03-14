document.addEventListener("DOMContentLoaded", function () {
    // Hent data når siden lastes
    if (document.getElementById("varerTable")) {
        fetchVarer();
    }
    if (document.getElementById("kunderTable")) {
        fetchKunder();
    }
    if (document.getElementById("ordrerTable")) {
        fetchOrdrer();
    }

    // Legg til ny vare
    const addVareForm = document.getElementById("addVareForm");
    if (addVareForm) {
        addVareForm.addEventListener("submit", function (event) {
            event.preventDefault();
            addVare();
        });
    }

    // Legg til ny kunde
    const addKundeForm = document.getElementById("addCustomerForm");
    if (addKundeForm) {
        addKundeForm.addEventListener("submit", function (event) {
            event.preventDefault();
            addKunde();
        });
    }
});

// ✅ Funksjon: Hent varer fra API og vis i tabellen
function fetchVarer() {
    fetch("/api/varer")
        .then((response) => response.json())
        .then((data) => {
            if (!data || data.error) {
                console.error("API-feil:", data.error);
                return;
            }
            const tableBody = document.querySelector("#varerTable tbody");
            if (!tableBody) return;
            tableBody.innerHTML = "";
            data.forEach((vare) => {
                const row = document.createElement("tr");
                row.innerHTML = `<td>${vare.varenummer}</td><td>${vare.betegnelse}</td><td>${vare.pris} NOK</td><td>${vare.antall}</td>`;
                tableBody.appendChild(row);
            });
        })
        .catch((error) => console.error("❌ Feil ved henting av varer:", error));
}

// ✅ Funksjon: Hent kunder fra API og vis i tabellen
function fetchKunder() {
    fetch("/api/kunder")
        .then(response => response.json())
        .then(data => {
            if (!data || data.error) {
                console.error("API-feil:", data.error);
                return;
            }
            const tableBody = document.querySelector("#kunderTable tbody");
            if (!tableBody) return;
            tableBody.innerHTML = "";
            data.forEach(kunde => {
                const row = `<tr><td>${kunde.knr}</td><td>${kunde.fornavn}</td><td>${kunde.etternavn}</td><td>${kunde.adresse}</td><td>${kunde.postnummer}</td></tr>`;
                tableBody.innerHTML += row;
            });
        })
        .catch(error => console.error("❌ Feil ved henting av kunder:", error));
}

// ✅ Funksjon: Hent ordrer fra API og vis i tabellen
function fetchOrdrer() {
    fetch("/api/ordrer")
        .then((response) => response.json())
        .then((data) => {
            if (!data || data.error) {
                console.error("API-feil:", data.error);
                return;
            }
            const tableBody = document.querySelector("#ordrerTable tbody");
            if (!tableBody) return;
            tableBody.innerHTML = "";
            data.forEach((ordre) => {
                const row = document.createElement("tr");
                row.innerHTML = `<td>${ordre.ordrenummer}</td><td>${ordre.ordre_dato}</td><td>${ordre.dato_sendt || "Ikke sendt"}</td><td>${ordre.betalt_dato || "Ikke betalt"}</td><td>${ordre.kundenavn}</td>`;
                tableBody.appendChild(row);
            });
        })
        .catch((error) => console.error("❌ Feil ved henting av ordrer:", error));
}

// ✅ Funksjon: Legg til en ny vare
function addVare() {
    const betegnelse = document.getElementById("betegnelse").value.trim();
    const pris = parseFloat(document.getElementById("pris").value);
    const antall = parseInt(document.getElementById("antall").value, 10);

    if (!betegnelse || isNaN(pris) || isNaN(antall) || pris <= 0 || antall < 0) {
        alert("⚠ Ugyldige verdier! Sjekk feltene og prøv igjen.");
        return;
    }

    fetch("/api/varer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ betegnelse, pris, antall }),
    })
    .then(response => response.json())
    .then(() => {
        location.reload(); // Oppdater siden
    })
    .catch(error => console.error("❌ Feil ved registrering av vare:", error));
}

// ✅ Funksjon: Legg til en ny kunde
function addKunde() {
    const fornavn = document.getElementById("fornavn").value.trim();
    const etternavn = document.getElementById("etternavn").value.trim();
    const adresse = document.getElementById("adresse").value.trim();
    const postnummer = parseInt(document.getElementById("postnummer").value, 10);
    const epost = document.getElementById("epost").value.trim();

    if (!fornavn || !etternavn || !adresse || isNaN(postnummer) || !validateEmail(epost)) {
        alert("⚠ Ugyldige verdier! Sjekk feltene og prøv igjen.");
        return;
    }

    fetch("/api/kunder", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fornavn, etternavn, adresse, postnummer, epost }),
    })
    .then(response => response.json())
    .then(() => {
        location.reload(); // Oppdater siden
    })
    .catch(error => console.error("❌ Feil ved registrering av kunde:", error));
}

// ✅ Funksjon: Sjekk om en e-post er gyldig
function validateEmail(email) {
    const pattern = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
    return pattern.test(email);
}
