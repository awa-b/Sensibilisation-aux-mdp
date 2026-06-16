document.addEventListener("DOMContentLoaded", () => {
    const passwordInput = document.getElementById("password-input");
    const toggleVisibilityBtn = document.getElementById("toggle-visibility");
    const analyzeBtn = document.getElementById("analyze-btn");
    const newTestBtn = document.getElementById("new-test-btn"); // Nouveau bouton
    const resultsSection = document.getElementById("results-section");
    const lengthSpan = document.getElementById("pwd-length");
    const classesSpan = document.getElementById("pwd-classes");
    const verdictSpan = document.getElementById("final-verdict");
    const mainReasons = document.getElementById("main-reasons");
    const actionableTips = document.getElementById("actionable-tips");
    const crackingProgress = document.getElementById("cracking-progress");
    const warning = document.getElementById("top-password-warning");
    const status  = document.getElementById("cracking-status");

    let source = null; // Variable pour stocker la connexion en cours

    toggleVisibilityBtn.addEventListener("click", () => {
        const isPassword = passwordInput.type === "password";
        passwordInput.type = isPassword ? "text" : "password";
        toggleVisibilityBtn.textContent = isPassword ? "🙈" : "👁️";
    });

    analyzeBtn.addEventListener("click", analyser);

    // --- NOUVEAU : Logique du bouton "Nouvelle analyse" ---
    if (newTestBtn) {
        newTestBtn.addEventListener("click", () => {
            // 1. Couper la connexion en cours si elle existe
            if (source) {
                source.close();
                source = null;
            }
            // 2. Vider le champ de mot de passe
            passwordInput.value = "";
            passwordInput.type = "password";
            toggleVisibilityBtn.textContent = "👁️";
            
            // 3. Cacher la section des résultats pour revenir à l'état initial
            resultsSection.classList.add("hidden");
        });
    }

    async function analyser(event) {
        const password = passwordInput.value;
        if (!password) return;

        // --- RÉINITIALISATION DE L'INTERFACE ---
        // Si une recherche était déjà en cours, on la coupe
        if (source) {
            source.close();
        }
        
        // On remet tout à zéro visuellement
        if (warning) warning.classList.add("hidden");
        if (status) status.textContent = "Test des mots du dictionnaire en cours...";
        document.getElementById("attempt-count").textContent = "0";
        document.getElementById("attempt-speed").textContent = "0";
        document.getElementById("current-candidate").textContent = "Démarrage de l'attaque...";
        if (crackingProgress) crackingProgress.style.width = "0%";
        
        verdictSpan.className = "";
        verdictSpan.textContent = "-";
        mainReasons.textContent = "";
        actionableTips.innerHTML = "";
        // --------------------------------------------------

        resultsSection.classList.remove("hidden");

        // Si le clic vient de l'utilisateur (pas du mode démo simulé)
        if (event && event.isTrusted) {
            
            // --- 1. Analyse théorique (Instantanée) ---
            const res = await fetch("/analyser", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mot_de_passe: password })
            });
            const data = await res.json();

            if (lengthSpan) lengthSpan.textContent = data.longueur;
            document.getElementById("pwd-entropy").textContent = data.entropie;
            document.getElementById("time-laptop").textContent = formaterTemps(data.temps_CPU);
            document.getElementById("time-gpu").textContent = formaterTemps(data.temps_GPU);

            const classes = [];
            if (data.minuscule) classes.push("a-z");
            if (data.majuscule) classes.push("A-Z");
            if (data.chiffre) classes.push("0-9");
            if (data.car_special) classes.push("Spé");
            if (classesSpan) classesSpan.textContent = classes.join(", ") || "-";

            // --- 2. Attaque en temps réel (Flux SSE) ---
            // Ouverture de la connexion en flux continu avec Flask
            source = new EventSource(`/recherche_stream?mot_de_passe=${encodeURIComponent(password)}`);

            source.onmessage = function(streamEvent) {
                const streamData = JSON.parse(streamEvent.data);

                // A. Mise à jour de l'animation pendant la recherche
                if (streamData.type === "progress") {
                    document.getElementById("attempt-count").textContent = streamData.tentatives.toLocaleString();
                    document.getElementById("attempt-speed").textContent = streamData.vitesse.toLocaleString();
                    document.getElementById("current-candidate").textContent = streamData.candidat;
                    
                    // Animation factice de la barre de progression (pour le visuel)
                    if(crackingProgress) {
                        let pourcentage = Math.min((streamData.tentatives / 200000) * 100, 100);
                        crackingProgress.style.width = `${pourcentage}%`;
                    }
                } 
                // B. Verdict final reçu
                else if (streamData.type === "result") {
                    source.close(); // On coupe proprement la connexion réseau
                    
                    if (streamData.trouve) {
                        if(crackingProgress) crackingProgress.style.width = "100%";
                        document.getElementById("current-candidate").textContent = `Cible trouvée : ${streamData.candidat}`;
                        
                        warning.classList.remove("hidden");
                        warning.textContent = `⚠️ Alerte : Votre mot de passe a été trouvé dans le dictionnaire en tant que "${streamData.candidat}".`;
                        status.textContent = "💀 Cassé par attaque dictionnaire.";
                        
                        updateVerdict("faible",
                            `Ce mot de passe est faible. Il a été déchiffré en ${streamData.tentatives.toLocaleString()} tentatives.`,
                            ["Ne jamais utiliser un mot de passe qui a déjà fuité.",
                             "Utilisez un gestionnaire de mots de passe pour en générer un unique."]
                        );
                    } else {
                        warning.classList.add("hidden");
                        document.getElementById("current-candidate").textContent = "— Fin du test —";
                        status.textContent = "✅ Absent de la liste des mots de passe fréquents.";
                        
                        if (data.entropie < 28) {
                            updateVerdict("faible", "Mot de passe trop court ou trop simple.", ["Utilisez au moins 12 caractères.", "Mélangez lettres, chiffres et symboles."]);
                        } else if (data.entropie < 60) {
                            updateVerdict("moyen", "Analyse basée sur l'entropie calculée.", ["Ajoutez des caractères spéciaux.", "Allongez encore un peu votre mot de passe."]);
                        } else {
                            updateVerdict("robuste", "Votre mot de passe est excellent ! Il résiste aux attaques par dictionnaire locales.", []);
                        }
                    }
                }
            };

            // Gestion des erreurs de connexion
            source.onerror = function() {
                source.close();
                document.getElementById("current-candidate").textContent = "Erreur de connexion avec le serveur.";
            };
        }
    }

    // Utilitaires de formatage et d'affichage
    function formaterTemps(secondes) {
        if (!secondes || secondes === 0) return "< 1 s";
        if (secondes < 60) return secondes + " s";
        if (secondes < 3600) return Math.round(secondes / 60) + " min";
        if (secondes < 86400) return Math.round(secondes / 3600) + " h";
        if (secondes < 2592000) return Math.round(secondes / 86400) + " jours";
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

    // Gestion du Menu Démo pour l'animateur
    const demoMenu = document.getElementById("demo-menu");
    const closeDemoBtn = document.getElementById("close-demo");
    const demoBtns = document.querySelectorAll(".demo-btn");

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
                        pwd: "123456", verdict: "faible",
                        reasons: "Ce mot de passe ne contient que des chiffres et est extrêmement court. Il est cassé instantanément car il est au sommet de toutes les listes de piratage connues.",
                        tips: ["Utilisez une longueur minimale de 12 caractères.", "Ne recyclez jamais une suite logique de clavier (azerty, 1234...)."]
                    },
                    "2": {
                        pwd: "Marseille2010!", verdict: "moyen",
                        reasons: "Bien qu'il utilise des majuscules, chiffres et caractères spéciaux, il est basé sur une prévisibilité humaine (nom propre + date). Il tombe très vite face à des attaques par dictionnaire intelligent (mutations).",
                        tips: ["Évitez absolument les noms propres, lieux, ou années de naissance.", "Ajouter un point d'exclamation à la fin est une astuce trop connue des pirates pour être efficace."]
                    },
                    "3": {
                        pwd: "correct horse battery staple", verdict: "robuste",
                        reasons: "Cette phrase de passe (passphrase) est excellente. L'absence de caractères spéciaux est largement compensée par son incroyable longueur. Elle résiste à toutes les attaques par force brute actuelles.",
                        tips: ["Privilégiez les phrases aléatoires composées de 4 mots sans rapport entre eux.", "Utilisez un gestionnaire de mots de passe ou des passkeys pour vos comptes critiques."]
                    }
                };

                const data = scenarios[scenario];
                if (data) {
                    passwordInput.value = data.pwd;
                    resultsSection.classList.remove("hidden");
                    updateVerdict(data.verdict, data.reasons, data.tips);
                }
            });
        });
    }
});