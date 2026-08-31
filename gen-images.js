const fs = require('fs');
const cards = JSON.parse(fs.readFileSync('C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards.json', 'utf8'));

function makeCardImage(name, cost, type) {
  const bgColor = type === '生物' ? '1e3a5f' : '3a1e5f';
  const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="250" height="350">' +
    '<rect width="250" height="350" rx="12" fill="#' + bgColor + '"/>' +
    '<text x="125" y="40" text-anchor="middle" fill="#fff" font-size="16" font-family="Arial">Cost: ' + cost + '</text>' +
    '<text x="125" y="175" text-anchor="middle" fill="#fff" font-size="14" font-family="Arial">' + name.substring(0,20) + '</text>' +
    '<text x="125" y="320" text-anchor="middle" fill="#aaa" font-size="12" font-family="Arial">' + type + '</text>' +
    '</svg>';
  return 'data:image/svg+xml;base64,' + Buffer.from(svg).toString('base64');
}

for (const [id, card] of Object.entries(cards)) {
  card.face.front.image = makeCardImage(card.name, card.cost, card.type);
}

fs.writeFileSync('C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards.json', JSON.stringify(cards), 'utf8');
console.log('Generated inline SVG images for', Object.keys(cards).length, 'cards');
