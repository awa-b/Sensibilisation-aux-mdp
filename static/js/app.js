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
  const crackingProgress = document.getElementById("cracking-progress");
  const warning = document.getElementById("top-password-warning");
  const status = document.getElementById("cracking-status");

  let source = null;
  let startTime = 0;

  // État pour éviter le spam de clics
  let isCurrentlyAnalyzing = false;

  toggleVisibilityBtn.addEventListener("click", () => {
    const isPassword = passwordInput.type === "password";
    passwordInput.type = isPassword ? "text" : "password";
    toggleVisibilityBtn.textContent = isPassword ? "🙈" : "👁️";
  });

  // --- LOGIQUE DU BOUTON PRINCIPAL (LANCEMENT DIRECT) ---
  analyzeBtn.addEventListener("click", async (event) => {
    if (isCurrentlyAnalyzing) return; // Empêche de spammer le bouton

    const password = passwordInput.value;
    if (!password) return; // Si le champ est vide, on ne fait rien

    isCurrentlyAnalyzing = true;
    analyzeBtn.textContent = "LANCER UNE NOUVELLE ANALYSE";

    // Bloque légèrement l'opacité du bouton pendant le calcul réseau
    analyzeBtn.style.opacity = "0.5";

    try {
      await runAnalysis(event, password);
    } finally {
      // Quoi qu'il arrive, on débloque le bouton à la fin
      isCurrentlyAnalyzing = false;
      analyzeBtn.style.opacity = "1";
    }
  });

  function resetInterface() {
    if (source) {
      source.close();
      source = null;
    }

    passwordInput.value = "";
    passwordInput.type = "password";
    toggleVisibilityBtn.textContent = "👁️";
    resultsSection.classList.add("hidden");

    const hashSpan = document.getElementById("pwd-hash");
    if (hashSpan) hashSpan.textContent = "-";

    analyzeBtn.textContent = "ANALYSER";

    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function runAnalysis(event, password) {
    // --- NETTOYAGE IMMÉDIAT DE L'INTERFACE AVANT LA NOUVELLE RECHERCHE ---
    if (source) source.close();

    if (warning) warning.classList.add("hidden");
    if (status)
      status.textContent = "Test des mots du dictionnaire en cours...";
    document.getElementById("attempt-count").textContent = "0";
    document.getElementById("attempt-speed").textContent = "0";
    document.getElementById("current-candidate").textContent =
      "Démarrage de l'attaque...";
    if (crackingProgress) crackingProgress.style.width = "0%";

    verdictSpan.className = "";
    verdictSpan.textContent = "-";
    mainReasons.textContent = "";
    actionableTips.innerHTML = "";

    const hashSpan = document.getElementById("pwd-hash");
    if (hashSpan) hashSpan.textContent = "-"; // On efface l'ancien hash

    resultsSection.classList.remove("hidden");

    if (event && event.isTrusted) {
      // --- 1. ENVOI DU MOT DE PASSE AU SERVEUR POUR ANALYSE ---
      const res = await fetch("/analyser", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mot_de_passe: password }),
      });
      const data = await res.json();// --- 2. RÉCEPTION DES DONNÉES DU SERVEUR ---

      const tokenSecurise = data.token;//

      // Mise à jour du bloc Théorique
      if (lengthSpan) lengthSpan.textContent = data.longueur;
      document.getElementById("pwd-entropy").textContent = data.entropie;
      document.getElementById("time-laptop").textContent = formaterTemps(
        data.temps_CPU,
      );
      document.getElementById("time-gpu").textContent = formaterTemps(
        data.temps_GPU,
      );

      const classes = [];// On construit la liste des classes de caractères utilisées
      if (data.minuscule) classes.push("a-z");
      if (data.majuscule) classes.push("A-Z");
      if (data.chiffre) classes.push("0-9");
      if (data.car_special) classes.push("Spé");
      if (classesSpan) classesSpan.textContent = classes.join(", ") || "-";

      if (hashSpan) hashSpan.textContent = data.hash_md5;

      // --- 3. ATTAQUE EN TEMPS RÉEL SÉCURISÉE (SSE) ---
      startTime = Date.now();

      source = new EventSource(`/recherche_stream?token=${tokenSecurise}`);

      source.onmessage = function (streamEvent) {
        const streamData = JSON.parse(streamEvent.data);

        if (streamData.type === "progress") {
          document.getElementById("attempt-count").textContent =
            streamData.tentatives.toLocaleString();
          document.getElementById("attempt-speed").textContent =
            streamData.vitesse.toLocaleString();
          document.getElementById("current-candidate").textContent =
            streamData.candidat;

          if (crackingProgress) {
            let pourcentage = Math.min(
              (streamData.tentatives / 143000000) * 100,
              100,
            );
            crackingProgress.style.width = `${pourcentage}%`;
          }
        } else if (streamData.type === "result") {
          source.close();

          const tempsEcoule = ((Date.now() - startTime) / 1000).toFixed(1);

          if (streamData.trouve) {
            if (crackingProgress) crackingProgress.style.width = "100%";
            document.getElementById("current-candidate").textContent =
              `Cible trouvée : ${streamData.candidat}`;

            warning.classList.remove("hidden");
            warning.textContent = `⚠️  : Votre mot de passe a été trouvé dans le dictionnaire en tant que "${streamData.candidat}".`;
            status.textContent = `💀 Cassé par : ${streamData.methode}`;

            let explication = `Il a été déchiffré en ${streamData.tentatives.toLocaleString()} tentatives (Temps : ${tempsEcoule} s).`;
            if (streamData.rang) {
              explication += `\n\n🚨  : Ce mot de passe est le n° ${streamData.rang.toLocaleString()} des mots de passe les plus utilisés au monde !\n\n`;
            }

            if (data.temps_CPU > 86400) {
              explication += `\n\nL'illusion de la longueur : En théorie, ce mot de passe aurait dû tenir ${formaterTemps(data.temps_CPU)}. Mais parce qu'il utilise des mots du dictionnaire ou un schéma prévisible, l'attaque intelligente l'a pulvérisé.`;
            }

            let conseilsSurMesure = [
              "Ne recyclez jamais un mot de passe qui a déjà fuité.",
              "Privilégiez par exemple les phrases de passe (4 mots aléatoires sans rapport).",
            ];

            if (/\d{4}$/.test(password)) {
              conseilsSurMesure.unshift(
                "Évitez d'ajouter une année (ex: 2026) à la fin d'un mot, c'est le premier test des pirates.",
              );
            } else if (
              /^[A-Z][a-z]+/.test(password) &&
              /\d+!?$/.test(password)
            ) {
              conseilsSurMesure.unshift(
                "Le schéma 'Majuscule au début + Mot + Chiffres/Symbole à la fin' est trop facile à deviner.",
              );
            }

            updateVerdict("faible", explication, conseilsSurMesure);
          } else {
            warning.classList.add("hidden");
            document.getElementById("current-candidate").textContent =
              "— Fin du dictionnaire —";
            status.textContent = `✅ Absent de la liste complète (Recherche terminée en ${tempsEcoule} s).`;

            if (data.entropie < 28) {
              updateVerdict(
                "faible",
                "Mot de passe trop court ou trop simple.",
                [
                  "Utilisez au moins 12 caractères.",
                  "Mélangez lettres, chiffres et symboles.",
                ],
              );
            } else if (data.entropie < 60) {
              updateVerdict("moyen", "Analyse basée sur l'entropie calculée.", [
                "Ajoutez des caractères spéciaux.",
                "Allongez encore un peu votre mot de passe.",
              ]);
            } else {
              updateVerdict(
                "robuste",
                "Votre mot de passe est excellent ! Il résiste à nos attaques par dictionnaire.",
                [],
              );
            }
          }
        }
      };

      source.onerror = function () {
        source.close();
        document.getElementById("current-candidate").textContent =
          "Erreur de connexion avec le serveur.";
      };
    }
  }

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
      faible: { text: "FAIBLE", class: "verdict-faible" },
      moyen: { text: "MOYEN", class: "verdict-moyen" },
      robuste: { text: "ROBUSTE", class: "verdict-robuste" },
    };

    if (verdicts[verdictType]) {
      verdictSpan.textContent = verdicts[verdictType].text;
      verdictSpan.classList.add(verdicts[verdictType].class);
    }

    mainReasons.textContent = reasons;
    tips.forEach((tip) => {
      const li = document.createElement("li");
      li.textContent = `💡 ${tip}`;
      actionableTips.appendChild(li);
    });
  }

  // --- Gestion du Menu Démo pour l'animateur ---
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
    demoBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        const scenario = btn.getAttribute("data-scenario");
        demoMenu.classList.add("hidden");

        const scenarios = {
          1: {
            pwd: "123456",
            verdict: "faible",
            reasons:
              "Ce mot de passe ne contient que des chiffres et est extrêmement court. Il est cassé instantanément car il est au sommet de toutes les listes de piratage connues.",
            tips: [
              "Utilisez une longueur minimale de 12 caractères.",
              "Ne recyclez jamais une suite logique de clavier (azerty, 1234...).",
            ],
          },
          2: {
            pwd: "Marseille2010!",
            verdict: "moyen",
            reasons:
              "Bien qu'il utilise des majuscules, chiffres et caractères spéciaux, il est basé sur une prévisibilité humaine (nom propre + date). Il tombe très vite face à des attaques par dictionnaire intelligent (mutations).",
            tips: [
              "Évitez absolument les noms propres, lieux, ou années de naissance.",
              "Ajouter un point d'exclamation à la fin est une astuce trop connue des pirates pour être efficace.",
            ],
          },
          3: {
            pwd: "correct horse battery staple",
            verdict: "robuste",
            reasons:
              "Cette phrase de passe (passphrase) est excellente. L'absence de caractères spéciaux est largement compensée par son incroyable longueur. Elle résiste à toutes les attaques par force brute actuelles.",
            tips: [
              "Privilégiez les phrases aléatoires composées de 4 mots sans rapport entre eux.",
              "Utilisez un gestionnaire de mots de passe ou des passkeys pour vos comptes critiques.",
            ],
          },
        };

        const data = scenarios[scenario];
        if (data) {
          resetInterface(); // Utile ici pour tout vider
          passwordInput.value = data.pwd;
          resultsSection.classList.remove("hidden");

          analyzeBtn.textContent = "NOUVELLE ANALYSE";

          updateVerdict(data.verdict, data.reasons, data.tips);
        }
      });
    });
  }
});
