import re
path = '/Users/mickaeldarmon/Desktop/RBI.html/traites.html'
content = open(path,'r',encoding='utf-8').read()

# Trouver la carte GLRMI par son début exact
start = content.find('onclick="openLb(\'glrmi\')"')
if start < 0:
    print("GLRMI non trouvee"); exit()

# Remonter au debut du div
start = content.rfind('<div class="t-card"', 0, start)

# Trouver la fin : deux </div> imbriqués
end = content.find('</div>', start)
end = content.find('</div>', end+1) + len('</div>')

carte = content[start:end]
print("Carte extraite:", len(carte), "chars")

# Supprimer la carte de sa position actuelle
content = content[:start] + content[end:]

# Retrouver la position d'insertion : avant la section amerique
idx = content.find('data-cont="amerique"')
chunk = content[:idx]
pos = chunk.rfind('</div>\n      </div>') + len('</div>\n      </div>')
content = content[:pos] + '\n      ' + carte + content[pos:]

open(path,'w',encoding='utf-8').write(content)
print("OK GLRMI insere dans grille France")
