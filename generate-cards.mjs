import fs from 'fs'
import path from 'path'

const DECK_DIR = 'C:/Users/layja/obsidian/worldbuilding/card-game'
const OUTPUT = 'C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards.json'

const DECK_FILES = [
  { file: '預組A-主角組·觀測之眼.md', prefix: 'pa', faction: '實驗體' },
  { file: '預組B-清理組·暗紅色者.md', prefix: 'pb', faction: '認知科學局' },
  { file: '預組C-回聖會·先知之歌.md', prefix: 'pc', faction: '回聖會' },
  { file: '預組D-歸獸者·野性本能.md', prefix: 'pd', faction: '歸獸者' }
]

function parseDeckFile(filePath, prefix, faction) {
  const content = fs.readFileSync(filePath, 'utf-8')
  const cards = []
  const lines = content.split('\n')
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    // Match: | # | **Name** | cost | ...
    const match = line.match(/^\|\s*(\d+)\s*\|\s*\*\*(.+?)\*\*\s*\|\s*(\d+)\s*\|/)
    if (!match) continue
    
    const num = match[1]
    const name = match[2].trim()
    const cost = parseInt(match[3])
    
    const cols = line.split('|').map(c => c.trim()).filter(c => c)
    
    let type = '法術'
    let atk = null
    let hp = null
    let ability = ''
    
    if (cols.length >= 6) {
      const atkVal = cols[3]
      const hpVal = cols[4]
      if (!isNaN(parseInt(atkVal)) && !isNaN(parseInt(hpVal)) && atkVal !== '') {
        type = '生物'
        atk = parseInt(atkVal)
        hp = parseInt(hpVal)
        ability = cols[5] || ''
      } else {
        ability = cols[4] || ''
      }
    } else if (cols.length >= 5) {
      ability = cols[4] || cols[3] || ''
    }
    
    const id = `${prefix}_${num.padStart(2, '0')}`
    
    cards.push({
      id,
      face: {
        front: {
          name: { name },
          type,
          cost,
          image: ''
        }
      },
      name,
      type,
      cost,
      faction,
      atk,
      hp,
      ability: ability.replace(/\*\*/g, '').replace(/\|/g, '').trim()
    })
  }
  
  return cards
}

function main() {
  const allCards = {}
  
  for (const deck of DECK_FILES) {
    const filePath = path.join(DECK_DIR, deck.file)
    
    if (!fs.existsSync(filePath)) {
      console.log(`File not found: ${filePath}`)
      continue
    }
    
    const cards = parseDeckFile(filePath, deck.prefix, deck.faction)
    for (const card of cards) {
      allCards[card.id] = card
    }
    console.log(`${deck.file}: ${cards.length} cards (prefix: ${deck.prefix})`)
  }
  
  fs.writeFileSync(OUTPUT, JSON.stringify(allCards, null, 2))
  console.log(`\nTotal unique cards: ${Object.keys(allCards).length}`)
}

main()
