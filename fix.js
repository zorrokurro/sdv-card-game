const fs = require('fs');
const cards = JSON.parse(fs.readFileSync('C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards.json', 'utf8'));

// Minimal 1x1 transparent PNG as data URI
const img = 'data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22250%22%20height%3D%22350%22%3E%3Crect%20width%3D%22250%22%20height%3D%22350%22%20fill%3D%22%232a2a4a%22%2F%3E%3C%2Fsvg%3E';

for (const card of Object.values(cards)) {
  card.face.front.image = img;
}

fs.writeFileSync('C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards.json', JSON.stringify(cards, null, 2), 'utf8');
console.log('Size:', fs.statSync('C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards.json').size);
