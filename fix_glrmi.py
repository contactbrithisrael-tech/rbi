import re
path = '/Users/mickaeldarmon/Desktop/RBI.html/traites.html'
content = open(path,'r',encoding='utf-8').read()

m = re.search(r'<div class="t-card" onclick="openLb\(\'glrmi\'\)".*?</div>\s*</div>', content, re.DOTALL)
if not m:
    print("GLRMI non trouvee"); exit()
carte = m.group(0)
content = content.replace(carte, '')

idx = content.find('data-cont="amerique"')
chunk = content[:idx]
pos = chunk.rfind('</div>\n      </div>') + len('</div>\n      </div>')
content = content[:pos] + '\n      ' + carte + content[pos:]

open(path,'w',encoding='utf-8').write(content)
print("OK GLRMI insere dans grille France")
