#!/usr/bin/env python3
"""
SEO Guide Étudiant
- Injecte un bloc <head> SEO complet dans chaque page HTML
- Génère sitemap.xml et robots.txt

Usage : placer ce fichier à la racine du site, modifier DOMAIN, puis :
    python3 seo.py
Relançable autant de fois que voulu (le bloc est remplacé, pas dupliqué).
"""
import re, json
from pathlib import Path
from datetime import date

# ====== À MODIFIER APRÈS L'HÉBERGEMENT ======
DOMAIN   = "https://www.tondomaine.fr"   # sans / à la fin
SITE     = "Guide Étudiant"
OG_IMAGE = "/img/apercu.png"             # 1200x630 px
COLOR    = "#1a0660"
# ============================================

# fichier : (titre ~60 car., description ~150 car., nom court, priorité)
PAGES = {
    "index.html": (
        "Guide Étudiant : démarches, bourses et logement expliqués simplement",
        "Bourse CROUS, CAF, logement, inscription, révisions : le guide étudiant qui explique les démarches en France étape par étape, sans jargon.",
        "Accueil", "1.0"),
    "a_propos.html": (
        "À propos du Guide Étudiant : un site fait par un étudiant",
        "Pourquoi le Guide Étudiant existe : rendre l'administratif et la vie étudiante en France enfin compréhensibles, par un étudiant pour les étudiants.",
        "À propos", "0.4"),
    "preparatifs.html": (
        "Préparer sa rentrée étudiante : checklist complète",
        "Tout ce qu'il faut préparer avant la rentrée à la fac : documents, inscription, logement, budget, matériel. Checklist simple étape par étape.",
        "Préparatifs", "0.8"),
    "taches_administratives.html": (
        "Démarches administratives étudiantes : le guide simple",
        "CVEC, inscription administrative, sécu, CAF : les démarches obligatoires des étudiants expliquées clairement, avec les pièges à éviter.",
        "Tâches administratives", "0.9"),
    "demarches.html": (
        "Démarches recommandées pour les étudiants en France",
        "Les démarches pas obligatoires mais très utiles quand on est étudiant : aides, réductions, comptes à créer. Le tout expliqué simplement.",
        "Démarches recommandées", "0.8"),
    "logement.html": (
        "Logement étudiant : CROUS, APL et bons plans pour se loger",
        "Trouver un logement étudiant : résidence CROUS, colocation, garant Visale, demande d'APL. Étapes, délais et arnaques à éviter.",
        "Logement", "0.9"),
    "courses.html": (
        "Budget étudiant et courses : manger bien sans se ruiner",
        "Faire ses courses et tenir son budget d'étudiant : restos U, astuces pour économiser, applis anti-gaspi et idées de repas pas chers.",
        "Budget & courses", "0.7"),
    "fac_systeme.html": (
        "Fonctionnement de la fac : ECTS, CM/TD, partiels et rattrapages",
        "Comment marche la fac : ECTS, compensation, CM, TD, TP, sessions de rattrapage, ENT et Moodle. Le système universitaire expliqué simplement.",
        "Fonctionnement de la fac", "0.9"),
    "aides_financieres.html": (
        "Aides financières étudiantes : bourse CROUS, APL, aides d'urgence",
        "Bourse CROUS, APL, aide d'urgence, repas à 1 € : toutes les aides financières pour étudiants, qui y a droit et comment les demander.",
        "Aides financières", "1.0"),
    "sante.html": (
        "Santé étudiante : sécu, mutuelle, CSS et service de santé",
        "Sécurité sociale, mutuelle, complémentaire santé solidaire, service de santé universitaire : se soigner quand on est étudiant, simplement.",
        "Santé", "0.8"),
    "transports.html": (
        "Transports étudiants : abonnements et réductions jeunes",
        "Abonnements bus, tram et train à tarif réduit pour étudiants : comment les obtenir et économiser sur ses trajets domicile–fac.",
        "Transports", "0.7"),
    "revision.html": (
        "Méthodes de révision efficaces pour réussir ses partiels",
        "Répétition espacée, active recall, Pomodoro, annales : les méthodes de révision qui marchent vraiment et un planning pour réussir ses partiels.",
        "Méthodes de révision", "0.9"),
    "jobs.html": (
        "Jobs étudiants : où trouver un job compatible avec les cours",
        "Trouver un job étudiant : sites, types de jobs compatibles avec les cours, contrat, heures max et prime d'activité. Guide pratique.",
        "Jobs étudiants", "0.8"),
    "vie_etudiante.html": (
        "Vie étudiante : assos, BDE, sport universitaire et sorties",
        "Assos, BDE, sport universitaire (SUAPS), culture et soirées : comment profiter de la vie étudiante et s'intégrer quand on ne connaît personne.",
        "Vie étudiante", "0.7"),
}

START, END = "<!-- SEO:START -->", "<!-- SEO:END -->"

# balises gérées par le bloc -> supprimées ailleurs pour éviter les doublons
DUPES = [
    r"<title>.*?</title>",
    r"<meta\s+charset[^>]*>",
    r"<meta\s+name=[\"'](description|viewport|robots|theme-color|twitter:[^\"']+)[\"'][^>]*>",
    r"<meta\s+property=[\"']og:[^\"']+[\"'][^>]*>",
    r"<link\s+rel=[\"']canonical[\"'][^>]*>",
]

def url_of(f):
    return f"{DOMAIN}/" if f == "index.html" else f"{DOMAIN}/{f}"

def block(f, title, desc, name):
    url, img = url_of(f), DOMAIN + OG_IMAGE
    if f == "index.html":
        ld = {"@context": "https://schema.org", "@type": "WebSite",
              "name": SITE, "url": url, "inLanguage": "fr-FR", "description": desc}
    else:
        ld = {"@context": "https://schema.org", "@type": "BreadcrumbList",
              "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{DOMAIN}/"},
                  {"@type": "ListItem", "position": 2, "name": name, "item": url}]}
    return f"""{START}
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{SITE}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{img}">
  <meta property="og:locale" content="fr_FR">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="{COLOR}">
  <link rel="icon" href="/favicon.ico">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
  {END}"""

def process(path, f, data):
    html = path.read_text(encoding="utf-8")
    html = re.sub(re.escape(START) + r".*?" + re.escape(END), "", html, flags=re.S)
    head = re.search(r"<head[^>]*>(.*?)</head>", html, flags=re.S | re.I)
    if not head:
        print(f"  ✗ {f} : pas de <head>, ignoré"); return False
    inner = head.group(1)
    for p in DUPES:
        inner = re.sub(p, "", inner, flags=re.S | re.I)
    inner = re.sub(r"\n\s*\n+", "\n", inner)
    new_head = head.group(0).replace(head.group(1), "\n  " + block(f, *data[:3]) + inner.rstrip() + "\n")
    html = html.replace(head.group(0), new_head)
    # lang="fr"
    if re.search(r"<html(?![^>]*\blang=)", html, flags=re.I):
        html = re.sub(r"<html", '<html lang="fr"', html, count=1, flags=re.I)
    else:
        html = re.sub(r'(<html[^>]*\blang=)["\'][^"\']*["\']', r'\1"fr"', html, count=1, flags=re.I)
    path.write_text(html, encoding="utf-8")
    print(f"  ✓ {f}"); return True

def main():
    root = Path(__file__).parent
    done = []
    print("Pages :")
    for f, data in PAGES.items():
        p = root / f
        if not p.exists():
            print(f"  ⚠ {f} introuvable (renomme la clé dans PAGES)"); continue
        if process(p, f, data): done.append((f, data[3]))
    for h in sorted(root.glob("*.html")):
        if h.name not in PAGES:
            print(f"  ? {h.name} n'est pas dans PAGES (ajoute-le)")

    today = date.today().isoformat()
    urls = "".join(f"  <url>\n    <loc>{url_of(f)}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>{pr}</priority>\n  </url>\n" for f, pr in done)
    (root / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
    (root / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n", encoding="utf-8")
    print(f"\n✓ sitemap.xml ({len(done)} pages)\n✓ robots.txt")
    if "tondomaine" in DOMAIN:
        print("\n⚠ Pense à remplacer DOMAIN par ton vrai domaine puis relance.")

if __name__ == "__main__":
    main()
