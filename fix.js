const fs = require('fs');
const cards = JSON.parse(fs.readFileSync('C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards.json', 'utf8'));
const baseUrl = 'https://zorrokurro.github.io/sdv-card-game/img/';

for (const card of Object.values(cards)) {
  card.face.front.image = baseUrl + card.id + '.svg';
}

fs.writeFileSync('C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards.json', JSON.stringify(cards, null, 2), 'utf8');
console.log('Updated', Object.keys(cards).length, 'cards with image URLs');
console.log('Size:', fs.statSync('C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards.json').size);
