document.addEventListener("DOMContentLoaded", function () {
    // Hent data når siden lastes
    if (document.getElementById("varerTable")) {
        fetchVarer(); // Denne er nå oppdatert
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
            addVare(); // Husk at denne må oppdateres for å sende VNr hvis du skal bruke den korrigerte add_vare i API-et
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

// Funksjon: Hent varer fra API og vis i tabellen (OPPDATERT)
function fetchVarer() {
    fetch("/api/varer")
        .then((response) => {
            if (!response.ok) { // Sjekk om status er OK (200-299)
                throw new Error(`Nettverksrespons var ikke ok: ${response.statusText}`);
            }
            return response.json();
        })
        .then((data) => {
            // API returnerer nå en liste (kan være tom) hvis OK
            const tableBody = document.querySelector("#varerTable tbody");
            if (!tableBody) {
                console.error("Kunne ikke finne table body for varerTable");
                return;
            }
            tableBody.innerHTML = ""; // Tøm tabellen før data legges inn

            if (!Array.isArray(data)) {
               console.error("Mottok ikke en liste fra /api/varer:", data);
               return; // Avslutt hvis data ikke er en liste
            }

            data.forEach((vare) => {
                const row = document.createElement("tr");
                // --- BRUKER NÅ KORREKTE NØKLER ---
                // (VNr, Betegnelse, Pris, Antall kommer fra API)
                const vnr = vare.VNr ?? 'N/A';
                const betegnelse = vare.Betegnelse ?? 'Ukjent';
                // Pris kommer som et tall (float) fra API
                const pris = vare.Pris ?? 0;
                const antall = vare.Antall ?? 0;

                // Formater prisen med to desimaler
                row.innerHTML = `<td>${vnr}</td><td>${betegnelse}</td><td>${pris.toFixed(2)} NOK</td><td>${antall}</td>`;
                tableBody.appendChild(row);
            });
        })
        .catch((error) => console.error("Feil ved henting av varer:", error));
}


// Funksjon: Hent kunder fra API og vis i tabellen
function fetchKunder() {
    fetch("/api/kunder")
        .then(response => response.json())
        .then(data => {
            // Forbedret feilsjekk
            if (!response.ok) {
               throw new Error(`Nettverksrespons var ikke ok: ${response.statusText}`);
            }
            if (!Array.isArray(data)) { // Sjekk om data er en liste
                console.error("Mottok ikke en liste fra /api/kunder:", data);
                // Håndter feil, f.eks. vis en melding til brukeren
                const tableBody = document.querySelector("#kunderTable tbody");
                if (tableBody) tableBody.innerHTML = '<tr><td colspan="5">Kunne ikke laste kundedata.</td></tr>';
                return;
            }

            const tableBody = document.querySelector("#kunderTable tbody");
            if (!tableBody) {
                console.error("Kunne ikke finne table body for kunderTable");
                return;
            }
            tableBody.innerHTML = ""; // Tøm tabellen

            data.forEach(kunde => {
                // Bruker korrekte feltnavn fra databasen (store/små bokstaver)
                const knr = kunde.KNr ?? 'N/A';
                const fornavn = kunde.Fornavn ?? '';
                const etternavn = kunde.Etternavn ?? '';
                const adresse = kunde.Adresse ?? '';
                const postnr = kunde.PostNr ?? '';
                const row = `<tr><td>${knr}</td><td>${fornavn}</td><td>${etternavn}</td><td>${adresse}</td><td>${postnr}</td></tr>`;
                tableBody.innerHTML += row; // Bruk appendChild for bedre ytelse hvis mulig, men += fungerer
            });
        })
        .catch(error => {
            console.error("Feil ved henting av kunder:", error);
            const tableBody = document.querySelector("#kunderTable tbody");
            if (tableBody) tableBody.innerHTML = `<tr><td colspan="5">Feil: ${error.message}</td></tr>`;
        });
}

// Funksjon: Hent ordrer fra API og vis i tabellen
function fetchOrdrer() {
    fetch("/api/ordrer")
        .then((response) => {
            if (!response.ok) {
                throw new Error(`Nettverksrespons var ikke ok: ${response.statusText}`);
            }
            return response.json();
        })
        .then((data) => {
            const tableBody = document.querySelector("#ordrerTable tbody");
            if (!tableBody) {
                console.error("Fant ikke tbody i #ordrerTable");
                return;
            }

            tableBody.innerHTML = "";

            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="5">Ingen ordrer funnet.</td></tr>';
                return;
            }

            data.forEach((ordre) => {
                const ordrenummer = ordre.OrdreNr ?? "Ukjent";
                const ordredato = ordre.OrdreDato ?? "Ukjent";
                const sendtDato = ordre.SendtDato ?? "Ikke sendt";
                const betaltDato = ordre.BetaltDato ?? "Ikke betalt";
                const kundenavn = ordre.Kundenavn ?? "Ukjent";

                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${ordrenummer}</td>
                    <td>${ordredato}</td>
                    <td>${sendtDato}</td>
                    <td>${betaltDato}</td>
                    <td>${kundenavn}</td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch((error) => {
            console.error("Feil ved henting av ordrer:", error);
            const tableBody = document.querySelector("#ordrerTable tbody");
            if (tableBody)
                tableBody.innerHTML = `<tr><td colspan="5">Feil ved lasting av ordrer: ${error.message}</td></tr>`;
        });
}

// Funksjon: Legg til en ny vare
function addVare() {
    // Husk å legge til et input-felt for 'vnr' i varer.html
    const vnrInput = document.getElementById("vnr"); // Antatt ID for nytt felt
    if (!vnrInput) {
        alert("FEIL: Input-felt for VNr mangler i HTML.");
        return;
    }
    const vnr = vnrInput.value.trim();
    const betegnelse = document.getElementById("betegnelse").value.trim();
    const pris = parseFloat(document.getElementById("pris").value);
    const antall = parseInt(document.getElementById("antall").value, 10);

    // Legg til VNr i valideringen
    if (!vnr || !betegnelse || isNaN(pris) || isNaN(antall) || pris <= 0 || antall < 0) {
        alert("Ugyldige verdier! Sjekk alle feltene (VNr, Betegnelse, Pris, Antall) og prøv igjen.");
        return;
    }

    // Send med 'vnr' i JSON-bodyen
    fetch("/api/varer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ vnr, betegnelse, pris, antall }), // Sender vnr
    })
    .then(async response => { // Bruk async for å enkelt hente JSON ved feil
        const isJson = response.headers.get('content-type')?.includes('application/json');
        const data = isJson ? await response.json() : null;

        // Sjekk for feil fra API-et
        if (!response.ok) {
            // Få feilmelding fra data hvis mulig, ellers bruk statusText
            const error = (data && data.error) || response.statusText;
            throw new Error(error); // Kast feil for å gå til .catch
        }
        // Hvis OK (201 Created), last inn varer på nytt
        fetchVarer(); // Oppdater tabellen dynamisk i stedet for å laste hele siden på nytt
        // Tøm skjemaet
        document.getElementById("addVareForm").reset();

    })
    // .then(() => {
    //     location.reload(); // Unngå reload, oppdater heller tabellen med fetchVarer()
    // })
    .catch(error => {
         console.error("Feil ved registrering av vare:", error);
         alert(`Kunne ikke legge til vare: ${error.message}`); // Vis feilmelding til bruker
    });
}

// Funksjon: Legg til en ny kunde
function addKunde() {
    // Antar at API /api/kunder for POST ikke finnes ennå,
    // eller at den skal implementeres for å håndtere dette.
    // Denne koden sender data, men API-et må være klart til å motta det.
    const fornavn = document.getElementById("fornavn").value.trim();
    const etternavn = document.getElementById("etternavn").value.trim();
    const adresse = document.getElementById("adresse").value.trim();
    const postnummer = document.getElementById("postnummer").value.trim(); // Send som string, DB tar CHAR(4)
    const epostInput = document.getElementById("epost"); // Valgfritt epost-felt?
    const epost = epostInput ? epostInput.value.trim() : null;

    if (!fornavn || !etternavn || !adresse || !postnummer) { // Fjernet epost fra påkrevd her
        alert("Ugyldige verdier! Fornavn, Etternavn, Adresse og Postnummer må fylles ut.");
        return;
    }
    // Valider epost hvis feltet finnes og er fylt ut
    if (epost && !validateEmail(epost)) {
         alert("Ugyldig e-postformat!");
         return;
    }

    // Merk: Sender feltnavn med små bokstaver til APIet.
    // API-endpoint for POST /kunder må matche dette eller justeres.
    const kundeData = { fornavn, etternavn, adresse, postnummer };
    if (epost) {
        kundeData.epost = epost; // Legg til epost hvis den finnes
    }

    fetch("/api/kunder", { // Antar at POST /api/kunder finnes og håndterer dette
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(kundeData),
    })
    .then(async response => {
        const isJson = response.headers.get('content-type')?.includes('application/json');
        const data = isJson ? await response.json() : null;

        if (!response.ok) {
            const error = (data && data.error) || response.statusText;
            throw new Error(error);
        }
        fetchKunder(); // Oppdater kundelisten
        document.getElementById("addCustomerForm").reset(); // Tøm skjemaet
    })
    .catch(error => {
        console.error("Feil ved registrering av kunde:", error);
        alert(`Kunne ikke legge til kunde: ${error.message}`);
    });
}

// Funksjon: Sjekk om en e-post er gyldig
function validateEmail(email) {
    const pattern = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
    return pattern.test(email);
}