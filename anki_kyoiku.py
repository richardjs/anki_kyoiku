import xml.etree.ElementTree as ET

import genanki


MAX_GRADE = 6


class Word:
    def __init__(self, word, reading, senses):
        self.word = word
        self.reading = reading
        self.senses = senses


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


print('loading data files...')

word_entries = {}
tree = ET.parse('data/JMdict_e')
root = tree.getroot()
for entry in root.findall('entry'):
    try:
        # we're only looking for the first kanji element, which should be the most common
        word = entry.find('k_ele').find('keb').text
    except:
        continue

    if not word:
        continue

    if word not in word_entries:
        word_entries[word] = []
    word_entries[word].append(entry)

kanji_list = []
words = {}
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
        # TODO add option to build for different languages
        if 'm_lang' in meaning.attrib:
            continue
        meanings.append(meaning.text)

    for line in open('data/wikipedia-20150422-lemmas.tsv'):
        if character not in line:
            continue
        word = line.split()[-1]
        # make sure we have a dictionary entry for the word before using it
        if word in word_entries:
            break

    kanji = Kanji(character, meanings, grade)
    kanji_list.append(kanji)
    words[word] = kanji

print('getting example word definitions...')

for word in word_entries.values():
    for entry in word:
        try:
            word = entry.find('k_ele').find('keb').text
        except:
            continue

        if word not in words:
            continue

        kanji = words[word]

        # just grabbing the first reb and r_ele should be fine
        reading = entry.find('r_ele').find('reb').text

        senses = []
        for sense in entry.findall('sense'):
            if sense.find('misc'):
                # misc indicates colloquialisms, usually kana usage, etc.
                # if the sense has this, we might just want to ignore it (to keep things simple)
                # TODO add options to include different misc attributes in the data
                continue
            sense_entry = ', '.join(
                gloss.text for gloss in sense.findall('gloss'))
            pos = sense.find('pos')
            if pos != None:
                sense_entry += ' <small><i>%s</i></small>' % sense.find(
                    'pos').text
            senses.append(sense_entry)

        kanji.add_word(Word(word, reading, senses))

print('building Anki package...')

grades = [[] for _ in range(MAX_GRADE)]
for kanji in kanji_list:
    grades[kanji.grade - 1].append(kanji)

for grade in grades:
    grade.sort()

kanji_model = genanki.Model(
    1698738421,
    '教育漢字',
    fields=[
        {'name': 'Kanji'},
        {'name': 'Meaning'},
        {'name': 'Example Word'},
        {'name': 'Example Word Entry'},
        {'name': 'Example Word Recording'},
        {'name': 'Decomposition'},
        {'name': 'Grade'},
    ],
    templates=[{
        'name': 'Kanji meaning',
        'qfmt': 'Meaning of:<br>{{Kanji}}',
        'afmt': '{{FrontSide}}<hr id="answer">{{Meaning}}<br><br><b>{{Example Word}}</b><br>{{Example Word Entry}}<br><br><small>grade {{Grade}}'
    }, {
        'name': 'Word reading',
        'qfmt': '{{#Example Word}}Reading for:<br>{{Example Word}}{{/Example Word}}',
        'afmt': '{{FrontSide}}<hr id="answer">{{Example Word Entry}}'
    }],
    css='''
        .card {
            font-family: arial;
            font-size: 20px;
            text-align: center;
            color: black;
            background-color: white;
        }
        table {
            margin: 0px auto;
        }
        td {
            border-top: 1px solid #555;
            border-bottom: 1px solid #555;
            padding: 3px;
            text-align: left;
        }
     '''
)

deck = genanki.Deck(
    1901981190,
    '教育漢字'
)

for grade in grades:
    for kanji in grade:
        example_word = ''
        if len(kanji.words) > 0:
            example_word = kanji.words[0].word
        example_entry = '<table>'
        for word in kanji.words:
            example_entry += '<tr>'
            example_entry += '<td>%s</td>' % word.reading
            example_entry += '<td>%s</td>' % '<br>'.join(word.senses)
            example_entry += '</tr>'
        example_entry += '</table>'

        note = KanjiNote(
            model=kanji_model,
            fields=[
                kanji.character,
                ', '.join(kanji.meanings),
                example_word,
                example_entry,
                # TODO: add Forvo recordings
                '',
                # TODO: add decomposition
                '',
                str(kanji.grade),
            ],
        )
        deck.add_note(note)

genanki.Package(deck).write_to_file('kyoiku.apkg')
