const fs = require('fs');
const path = require('path');
const cards = JSON.parse(fs.readFileSync('C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards.json', 'utf8'));
const dir = 'C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/img';
if (!fs.existsSync(dir)) fs.mkdirSync(dir, {recursive: true});

for (const card of Object.values(cards)) {
  const name = card.name || card.id;
  const type = card.type || '';
  const cost = card.cost || 0;
  const bgColor = type === '生物' ? '#2a4a6a' : '#6a2a4a';
  const typeColor = type === '生物' ? '#4a8ab5' : '#b54a7a';
  const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="250" height="350">' +
    '<rect width="250" height="350" rx="12" fill="' + bgColor + '"/>' +
    '<rect x="8" y="8" width="234" height="334" rx="8" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>' +
    '<rect x="0" y="0" width="250" height="40" rx="12" fill="' + typeColor + '"/>' +
    '<text x="125" y="27" text-anchor="middle" fill="white" font-size="14" font-family="Arial" font-weight="bold">' + name + '</text>' +
    '<text x="125" y="80" text-anchor="middle" fill="rgba(255,255,255,0.5)" font-size="11" font-family="Arial">' + type + ' | ' + cost + '</text>' +
    '<rect x="20" y="100" width="210" height="180" rx="6" fill="rgba(255,255,255,0.05)"/>' +
    '<text x="125" y="200" text-anchor="middle" fill="rgba(255,255,255,0.3)" font-size="48" font-family="Arial" font-weight="bold">' + cost + '</text>' +
    '</svg>';
  fs.writeFileSync(path.join(dir, card.id + '.svg'), svg, 'utf8');
}
console.log('Generated', Object.keys(cards).length, 'images in', dir);
