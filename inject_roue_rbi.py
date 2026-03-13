#!/usr/bin/env python3
"""
inject_roue_rbi.py  v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Injecte la Roue des 33 Degrés directement dans sitecomplet.html
(injection inline — aucune dépendance externe / aucun iframe nécessaire).

USAGE
─────
  1. Place ce script dans le même dossier que :
       • sitecomplet.html
       • roue_rbi_v7_FINAL.html
  2. Lance : python3 inject_roue_rbi.py
  3. Fichier produit : index_final.html  (prêt pour Netlify / Cloudflare)

ÉTAPES SUIVANTES
────────────────
  • Sur Netlify : glisse index_final.html dans le dashboard
  • Sur Cloudflare Worker : remplace flat-dust-a340 avec ce fichier
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import re, os, sys

SITE_FILE = "sitecomplet.html"
ROUE_FILE = "roue_rbi_v7_FINAL.html"
OUT_FILE  = "index_final.html"
WRAPPER   = "rbi-grades"

ANCHORS = [
    'id="traites"', 'id="traits"', 'class="traites"',
    '<!-- TRAITÉS -->', '<!-- TRAITES -->',
    'Les Traités Internationaux', 'Traités Internationaux',
]

NAV_LINK   = '<a href="#grades">Les Grades</a>'
NAV_BEFORE = '<a href="#traites">'


def scope_css(css_text, wrapper):
    css_text = re.sub(r':root\s*\{', f'.{wrapper}{{', css_text)
    css_text = re.sub(r'(?:html\s*,\s*body|html|body)\s*\{[^}]*\}', '', css_text, flags=re.DOTALL)
    css_text = re.sub(r'body::before\s*\{[^}]*\}', '', css_text, flags=re.DOTALL)

    result = []
    i = 0
    while i < len(css_text):
        # @keyframes / @font-face : copier tel quel
        m_at = re.match(r'(@(?:keyframes|font-face|charset|import)[^{]*\{)', css_text[i:], re.IGNORECASE)
        if m_at:
            start = i + m_at.end()
            depth, j = 1, start
            while j < len(css_text) and depth > 0:
                if css_text[j] == '{': depth += 1
                elif css_text[j] == '}': depth -= 1
                j += 1
            result.append(css_text[i:j])
            i = j
            continue

        # @media : préfixer sélecteurs internes
        m_media = re.match(r'(@media[^{]*)\{', css_text[i:], re.IGNORECASE)
        if m_media:
            query = m_media.group(1)
            start = i + m_media.end()
            depth, j = 1, start
            while j < len(css_text) and depth > 0:
                if css_text[j] == '{': depth += 1
                elif css_text[j] == '}': depth -= 1
                j += 1
            inner = css_text[start:j-1]
            inner_scoped = _prefix_selectors(inner, wrapper)
            result.append(f'{query}{{\n{inner_scoped}\n}}')
            i = j
            continue

        # Règle normale
        m_rule = re.match(r'([^{@][^{]*)\{([^}]*)\}', css_text[i:], re.DOTALL)
        if m_rule:
            sel_raw = m_rule.group(1).strip()
            body    = m_rule.group(2)
            if sel_raw:
                scoped_sel = ', '.join(
                    f'.{wrapper} {s.strip()}' for s in sel_raw.split(',') if s.strip()
                )
                result.append(f'{scoped_sel} {{{body}}}')
            i += m_rule.end()
            continue

        result.append(css_text[i])
        i += 1

    return '\n'.join(result)


def _prefix_selectors(css_block, wrapper):
    out = []
    for m in re.finditer(r'([^{@][^{]*)\{([^}]*)\}', css_block, re.DOTALL):
        sel_raw = m.group(1).strip()
        body    = m.group(2)
        if sel_raw:
            scoped = ', '.join(
                f'.{wrapper} {s.strip()}' for s in sel_raw.split(',') if s.strip()
            )
            out.append(f'{scoped} {{{body}}}')
    return '\n'.join(out)


def extract_roue(roue_html, wrapper):
    css_match = re.search(r'<style>(.*?)</style>', roue_html, re.DOTALL)
    raw_css   = css_match.group(1) if css_match else ''
    scoped_css = scope_css(raw_css, wrapper)

    body_match = re.search(r'<body>(.*?)</body>', roue_html, re.DOTALL)
    raw_body   = body_match.group(1) if body_match else ''

    js_match = re.search(r'<script>(.*?)</script>', roue_html, re.DOTALL)
    raw_js   = js_match.group(1) if js_match else ''

    return scoped_css, raw_body, raw_js


def build_section(scoped_css, raw_body, raw_js, wrapper):
    return f'''
<!-- ═══════════════════════════════════════════════════════════════════════
     SECTION : ROUE DES 33 DEGRÉS — RITE BRITH ISRAËL  (inject_roue_rbi v2)
     ═══════════════════════════════════════════════════════════════════════ -->
<section id="grades" style="background:#060810;padding:3rem 0 1rem;position:relative;overflow:hidden;">

  <div style="text-align:center;margin-bottom:2rem;">
    <h2 style="font-family:'Cinzel',serif;color:#D4AF37;font-size:clamp(1rem,2.5vw,1.6rem);
       letter-spacing:.35em;text-transform:uppercase;margin:0 0 .4rem;">
      ✡ Les 33 Degrés ✡
    </h2>
    <p style="font-family:'Cormorant Garamond',serif;font-style:italic;color:#9A8A6A;
       font-size:.95rem;letter-spacing:.15em;margin:0;">
      Structure Kabbalistique du Rite Brith Israël
    </p>
  </div>

  <style>
{scoped_css}
  </style>

  <div class="{wrapper}">
{raw_body}
  </div>

  <script>
(function(){{
{raw_js}
}})();
  </script>

</section>
<!-- ═══════════════════════════════════════════════════════════════════════ -->
'''


def inject():
    for f in [SITE_FILE, ROUE_FILE]:
        if not os.path.isfile(f):
            print(f"[ERREUR] Fichier introuvable : {f}")
            sys.exit(1)

    print(f"[OK] Lecture de {SITE_FILE}...")
    with open(SITE_FILE, 'r', encoding='utf-8') as f:
        site_html = f.read()

    print(f"[OK] Lecture de {ROUE_FILE}...")
    with open(ROUE_FILE, 'r', encoding='utf-8') as f:
        roue_html = f.read()

    if 'id="grades"' in site_html:
        print("[INFO] Section grades existante — remplacement...")
        site_html = re.sub(
            r'<!-- ═+\s*SECTION\s*:\s*ROUE DES 33.*?<!-- ═+[^>]*-->',
            '', site_html, flags=re.DOTALL)
        print("  [OK] Ancienne section supprimée.")

    print("[...] Extraction et scoping CSS...")
    scoped_css, raw_body, raw_js = extract_roue(roue_html, WRAPPER)
    section_html = build_section(scoped_css, raw_body, raw_js, WRAPPER)
    print("  [OK] Section construite.")

    if NAV_BEFORE in site_html:
        site_html = site_html.replace(NAV_BEFORE, NAV_LINK + '\n' + NAV_BEFORE, 1)
        print(f"[OK] Lien nav ajouté.")
    else:
        print(f"[INFO] Nav non trouvée — ajoute manuellement : {NAV_LINK}")

    anchor_pos, anchor_used = -1, None
    for pattern in ANCHORS:
        idx = site_html.find(pattern)
        if idx != -1:
            anchor_pos  = site_html.rfind('<', 0, idx)
            anchor_used = pattern
            break

    if anchor_pos == -1:
        print("[AVERT] Aucune ancre → injection avant </body>")
        site_html = site_html.replace('</body>', section_html + '\n</body>', 1)
    else:
        site_html = site_html[:anchor_pos] + section_html + site_html[anchor_pos:]
        print(f"[OK] Ancre : {repr(anchor_used)}")

    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write(site_html)

    size_mb = os.path.getsize(OUT_FILE) / 1_048_576
    print()
    print(f"✅  {OUT_FILE}  ({size_mb:.1f} MB)")
    print()
    print("━━━ ÉTAPES SUIVANTES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  NETLIFY    → Upload {OUT_FILE} sur tangerine-jelly-f494c8")
    print(f"  CLOUDFLARE → Remplace flat-dust-a340 avec {OUT_FILE}")
    print(f"  (Fichier unique — roue intégrée inline, aucune dépendance)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


if __name__ == '__main__':
    inject()
