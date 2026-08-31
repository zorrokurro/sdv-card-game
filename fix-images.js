const fs = require('fs');
const cards = JSON.parse(fs.readFileSync('C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards.json', 'utf8'));

const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="250" height="350"><rect width="250" height="350" rx="12" fill="#2a2a4a"/><text x="125" y="180" text-anchor="middle" fill="#fff" font-size="14">Card</text></svg>';
const img = 'data:image/svg+xml,' + encodeURIComponent(svg);

for (const card of Object.values(cards)) {
  card.face.front.image = img;
}

fs.writeFileSync('C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards.json', JSON.stringify(cards, null, 2), 'utf8');
console.log('File size:', fs.statSync('C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards.json').size, 'bytes');
