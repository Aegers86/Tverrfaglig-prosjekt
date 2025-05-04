// static/app.js
document.addEventListener("DOMContentLoaded", function () {
    // Hent data når siden lastes
    if (document.getElementById("varerTable")) {
        fetchVarer(); // Beholder henting av varer
    }

    // Legg til ny vare
    const addVareForm = document.getElementById("addVareForm");
    if (addVareForm) {
        addVareForm.addEventListener("submit", function (event) {
            event.preventDefault(); // Forhindre standard skjemainnsending
            addVare(); // Kall funksjon for å legge til vare via API
        });
    }
});

// Funksjon: Hent varer fra API og vis i tabellen
function fetchVarer() {
    fetch("/api/varer") // Bruker API-endepunktet (sjekk prefix i .env/app.py)
        .then((response) => {
            if (!response.ok) {
                throw new Error(`Nettverksrespons var ikke ok: ${response.statusText} (${response.status})`);
            }
            return response.json();
        })
        .then((data) => {
            const tableBody = document.querySelector("#varerTable tbody");
            if (!tableBody) {
                console.error("Kunne ikke finne table body for varerTable");
                return;
            }
            tableBody.innerHTML = ""; // Tøm tabellen før nye data legges inn

            if (!Array.isArray(data)) {
               console.error("Mottok ikke en liste fra /api/varer:", data);
               tableBody.innerHTML = '<tr><td colspan="4">Ugyldig data mottatt fra server.</td></tr>';
               return;
            }

            if (data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="4">Ingen varer funnet.</td></tr>';
                return;
            }

            data.forEach((vare) => {
                const row = document.createElement("tr");
                // Bruker korrekte nøkler fra API-responsen
                const vnr = vare.VNr ?? 'N/A';
                const betegnelse = vare.Betegnelse ?? 'Ukjent';
                const pris = vare.Pris ?? 0;
                const antall = vare.Antall ?? 0;

                // Formater prisen med to desimaler
                row.innerHTML = `<td>${vnr}</td><td>${betegnelse}</td><td>${pris.toFixed(2)} NOK</td><td>${antall}</td>`;
                tableBody.appendChild(row);
            });
        })
        .catch((error) => {
            console.error("Feil ved henting av varer:", error);
            const tableBody = document.querySelector("#varerTable tbody");
            if (tableBody) tableBody.innerHTML = `<tr><td colspan="4">Kunne ikke laste varer: ${error.message}</td></tr>`;
        });
}


// Funksjon: Legg til en ny vare via API
function addVare() {
    const vnrInput = document.getElementById("vnr");
    if (!vnrInput) {
        // Skal ikke skje hvis HTML er korrekt
        alert("FEIL: Intern feil - Input-felt for VNr mangler.");
        return;
    }
    const vnr = vnrInput.value.trim();
    const betegnelse = document.getElementById("betegnelse").value.trim();
    // Bruk parseFloat for å håndtere desimaltall for pris
    const pris = parseFloat(document.getElementById("pris").value);
    const antall = parseInt(document.getElementById("antall").value, 10);

    // Enkel validering
    if (!vnr || !betegnelse || isNaN(pris) || isNaN(antall) || pris <= 0 || antall < 0) {
        alert("Ugyldige verdier! Sjekk alle feltene (VNr, Betegnelse, Pris, Antall) og prøv igjen.");
        return;
    }

    // Send data til API-endepunktet
    fetch("/api/varer", { // Bruker API-endepunktet
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ vnr, betegnelse, pris, antall }), // Sender data som JSON
    })
    .then(async response => {
        const isJson = response.headers.get('content-type')?.includes('application/json');
        const data = isJson ? await response.json() : null;

        if (!response.ok) {
            // Prøv å få feilmelding fra API-respons, ellers bruk statusText
            const error = (data && data.error) || response.statusText;
            throw new Error(error); // Kast feil for å gå til .catch
        }
        // Hvis OK (f.eks. 201 Created)
        fetchVarer(); // Oppdater tabellen for å vise den nye varen
        document.getElementById("addVareForm").reset(); // Tøm skjemaet
    })
    .catch(error => {
         console.error("Feil ved registrering av vare:", error);
         // Gi brukeren beskjed
         alert(`Kunne ikke legge til vare: ${error.message}`);
    });
}