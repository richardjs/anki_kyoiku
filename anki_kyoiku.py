import xml.etree.ElementTree as ET

import genanki


MAX_GRADE = 6


class Word:
    def __init__(self, reading, gloss):
        self.reading = reading
        self.gloss = gloss


class Kanji:
    def __init__(self, character, meanings, grade):
        self.character = character
        self.meanings = meanings
        self.grade = grade
        self.words = []

    def add_word(self, word):
        self.words.append(word)

    def __lt__(self, other):
        return self.character < other.character


class KanjiNote(genanki.Note):
    @property
    def guid(self):
        return genanki.guid_for(self.fields[0])


print('loading kanji data...')

characters = {}

tree = ET.parse('data/kanjidic2.xml')
root = tree.getroot()
for entry in root.findall('character'):
    try:
        grade = int(entry.find('misc').find('grade').text)
    except:
        continue

    if grade > MAX_GRADE:
        continue

    character = entry.find('literal').text

    meanings = []
    for meaning in entry.find('reading_meaning').find('rmgroup').findall('meaning'):
        if 'm_lang' in meaning.attrib:
            continue
        meanings.append(meaning.text)

    characters[character] = Kanji(character, meanings, grade)

tree = ET.parse('data/JMdict_e')
root = tree.getroot()
for entry in root.findall('entry'):
    try:
        character = entry.find('k_ele').find('keb').text
    except:
        continue

    if character not in characters:
        continue

    kanji = characters[character]
    reading = entry.find('r_ele').find('reb').text
    gloss = entry.find('sense').find('gloss').text
    kanji.add_word(Word(reading, gloss))

grades = [[] for _ in range(MAX_GRADE)]
for k in characters.values():
    grades[k.grade - 1].append(k)

for grade in grades:
    grade.sort()

print('building Anki package...')

kanji_model = genanki.Model(
    1698738421,
    '教育漢字',
    fields=[
        {'name': 'Kanji'},
        {'name': 'Meaning'},
        {'name': 'Example Words'},
        {'name': 'Grade'},
    ],
    templates=[{
        'name': 'Kanji meaning',
        'qfmt': '{{Kanji}}',
        'afmt': '{{FrontSide}}<hr id="answer">{{Meaning}}<br><br>{{Example Words}}<br><small>grade {{Grade}}'
    }],
    css='''
	.card {
	    font-family: arial;
	    font-size: 20px;
	    text-align: center;
	    color: black;
	    background-color: white;
	}
    '''
)

deck = genanki.Deck(
    1901981190,
    '教育漢字'
)

for grade in grades:
    for kanji in grade:
        note = KanjiNote(
            model=kanji_model,
            fields=[
                kanji.character,
                ', '.join(kanji.meanings),
                '<table>'+'<tr>'.join(['<td>%s</td><td>%s</td>' % (word.reading, word.gloss)
                                       for word in kanji.words])+'</table>',
                str(kanji.grade),
            ],
        )
        deck.add_note(note)

genanki.Package(deck).write_to_file('kyoiku.apkg')
