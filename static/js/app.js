document.addEventListener("DOMContentLoaded", () => {

    const passwordInput = document.getElementById("password-input");
    const toggleVisibilityBtn = document.getElementById("toggle-visibility");
    const analyzeBtn = document.getElementById("analyze-btn");
    const resultsSection = document.getElementById("results-section");
    const lengthSpan = document.getElementById("pwd-length");
    const classesSpan = document.getElementById("pwd-classes");
    const verdictSpan = document.getElementById("final-verdict");
    const mainReasons = document.getElementById("main-reasons");
    const actionableTips = document.getElementById("actionable-tips");
    const demoMenu = document.getElementById("demo-menu");
    const closeDemoBtn = document.getElementById("close-demo");
    const demoBtns = document.querySelectorAll(".demo-btn");

    toggleVisibilityBtn.addEventListener("click", () => {
        const isPassword = passwordInput.type === "password";
        passwordInput.type = isPassword ? "text" : "password";
        toggleVisibilityBtn.textContent = isPassword ? "🙈" : "👁️";
    });

    analyzeBtn.addEventListener("click", analyser);

    async function analyser() {
    const password = passwordInput.value;
    if (!password) return;

    resultsSection.classList.remove("hidden");

    // 1. Analyse théorique
    const res = await fetch("/analyser", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mot_de_passe: password })
    });
    const data = await res.json();

    if (lengthSpan) lengthSpan.textContent = data.longueur;
    document.getElementById("pwd-entropy").textContent = data.entropie;
    document.getElementById("time-laptop").textContent = formaterTemps(data.temps_cpu);
    document.getElementById("time-gpu").textContent = formaterTemps(data.temps_gpu);

    const classes = [];
    if (data.classes.minuscule) classes.push("a-z");
    if (data.classes.majuscule) classes.push("A-Z");
    if (data.classes.chiffre) classes.push("0-9");
    if (data.classes.special) classes.push("Spé");
    if (classesSpan) classesSpan.textContent = classes.join(", ") || "-";

    // 2. Recherche dans dictionnaire
    const res2 = await fetch("/recherche", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mot_de_passe: password })
    });
    const data2 = await res2.json();

    const warning = document.getElementById("top-password-warning");
    const status  = document.getElementById("cracking-status");

    document.getElementById("attempt-count").textContent = data2.tentatives.toLocaleString();
    document.getElementById("attempt-speed").textContent = data2.vitesse.toLocaleString();
    document.getElementById("current-candidate").textContent = "— Fin du test —";

    // 3. Verdict (après avoir data ET data2)
    if (data2.trouve) {
        warning.classList.remove("hidden");
        if (data2.rang <=14344391){
            warning.textContent = `⚠️ Ce mot de passe est dans le top ${data2.rang} des mots de passe les plus utilisés au monde !`;
        } else {
            warning.textContent = `⚠️ Ce mot de passe est une variation connue d'un mot de passe fréquent !`;
        }
        status.textContent = "💀 Cassé instantanément par dictionnaire.";
        updateVerdict("faible",
            `Ce mot de passe est faible. Il est connu de tous les attaquants.`,
            ["Ne jamais utiliser un mot de passe qui a déjà fuité.",
             "Utilisez un gestionnaire de mots de passe pour en générer un unique."]
        );
    } else {
        warning.classList.add("hidden");
        status.textContent = "✅ Absent de la liste des mots de passe fréquents.";
        if (data.entropie < 28) {
            updateVerdict("faible", "Mot de passe trop court ou trop simple.", [
                "Utilisez au moins 12 caractères.",
                "Mélangez lettres, chiffres et symboles."
            ]);
        } else if (data.entropie < 60) {
            updateVerdict("moyen", "Analyse basée sur l'entropie calculée.", [
                "Ajoutez des caractères spéciaux.",
                "Allongez encore un peu votre mot de passe."
            ]);
        } else {
            updateVerdict("robuste",
                "Votre mot de passe est excellent ! Il résiste à toutes les attaques par force brute actuelles.", []);
        }
    }
}

    function formaterTemps(secondes) {
        if (secondes === 0) return "< 1 seconde";
        if (secondes < 60) return secondes + " s";
        if (secondes < 3600) return Math.round(secondes / 60) + " min";
        if (secondes < 86400) return Math.round(secondes / 3600) + " h";
        if (secondes < 2592000) return Math.round(secondes / 86400) + " jours";
        if (secondes < 31536000) return Math.round(secondes / 2592000) + " mois";
        return Math.round(secondes / 31536000) + " ans";
    }

    function updateVerdict(verdictType, reasons, tips) {
        verdictSpan.className = "";
        actionableTips.innerHTML = "";

        const verdicts = {
            "faible": { text: "FAIBLE", class: "verdict-faible" },
            "moyen": { text: "MOYEN", class: "verdict-moyen" },
            "robuste": { text: "ROBUSTE", class: "verdict-robuste" }
        };

        if (verdicts[verdictType]) {
            verdictSpan.textContent = verdicts[verdictType].text;
            verdictSpan.classList.add(verdicts[verdictType].class);
        }

        mainReasons.textContent = reasons;

        tips.forEach(tip => {
            const li = document.createElement("li");
            li.textContent = `💡 ${tip}`;
            actionableTips.appendChild(li);
        });
    }

    document.addEventListener("keydown", (e) => {
        if (e.ctrlKey && e.shiftKey && e.key.toUpperCase() === "D") {
            e.preventDefault();
            if (demoMenu) demoMenu.classList.toggle("hidden");
        }
    });

    if (closeDemoBtn) {
        closeDemoBtn.addEventListener("click", () => {
            demoMenu.classList.add("hidden");
        });
    }

    if (demoBtns) {
        demoBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                const scenario = btn.getAttribute("data-scenario");
                demoMenu.classList.add("hidden");

                const scenarios = {
                    "1": {
                        pwd: "123456",
                        verdict: "faible",
                        reasons: "Ce mot de passe ne contient que des chiffres et est extrêmement court. Il est cassé instantanément car il est au sommet de toutes les listes de piratage connues.",
                        tips: ["Utilisez une longueur minimale de 12 caractères.", "Ne recyclez jamais une suite logique de clavier (azerty, 1234...)."]
                    },
                    "2": {
                        pwd: "Marseille2010!",
                        verdict: "moyen",
                        reasons: "Bien qu'il utilise des majuscules, chiffres et caractères spéciaux, il est basé sur une prévisibilité humaine (nom propre + date). Il tombe très vite face à des attaques par dictionnaire intelligent (mutations).",
                        tips: ["Évitez absolument les noms propres, lieux, ou années de naissance.", "Ajouter un point d'exclamation à la fin est une astuce trop connue des pirates pour être efficace."]
                    },
                    "3": {
                        pwd: "correct horse battery staple",
                        verdict: "robuste",
                        reasons: "Cette phrase de passe (passphrase) est excellente. L'absence de caractères spéciaux est largement compensée par son incroyable longueur. Elle résiste à toutes les attaques par force brute actuelles.",
                        tips: ["Privilégiez les phrases aléatoires composées de 4 mots sans rapport entre eux.", "Utilisez un gestionnaire de mots de passe ou des passkeys pour vos comptes critiques."]
                    }
                };

                const data = scenarios[scenario];
                if (data) {
                    passwordInput.value = data.pwd;
                    analyzeBtn.click();
                    setTimeout(() => updateVerdict(data.verdict, data.reasons, data.tips), 500);
                }
            });
        });
    }
});