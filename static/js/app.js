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

    analyzeBtn.addEventListener("click", async () => {
        const password = passwordInput.value;
        if (!password) return;

        resultsSection.classList.remove("hidden");

        const response = await fetch('/analyser', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mot_de_passe: password })
        });

        const data = await response.json();
        console.log(data);
    
        if (lengthSpan) lengthSpan.textContent = data.longueur;
        if (document.getElementById('pwd-entropy')) {
        document.getElementById('pwd-entropy').textContent = data.entropie;
        }
        if (document.getElementById('time-laptop')) {
            document.getElementById('time-laptop').textContent = data.temps_CPU;
        }
        if (document.getElementById('time-gpu')) {
            document.getElementById('time-gpu').textContent = data.temps_GPU;
        }

        let classesUsed = [];
        if (data.minuscule) classesUsed.push("a-z");
        if (data.majuscule) classesUsed.push("A-Z");
        if (data.chiffre) classesUsed.push("0-9");
        if (data.car_special) classesUsed.push("Spé");
        if (classesSpan) classesSpan.textContent = classesUsed.join(", ");

        if (data.trouve) {
            document.getElementById('top-password-warning').classList.remove('hidden');
        }




        /*if (lengthSpan) lengthSpan.textContent = password.length;

        let classesUsed = [];
        if (/[a-z]/.test(password)) classesUsed.push("a-z");
        if (/[A-Z]/.test(password)) classesUsed.push("A-Z");
        if (/[0-9]/.test(password)) classesUsed.push("0-9");
        if (/[^a-zA-Z0-9]/.test(password)) classesUsed.push("Spé");

        if (classesSpan) {
            classesSpan.textContent = classesUsed.length > 0 ? classesUsed.join(", ") : "-";
        }*/
    });

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