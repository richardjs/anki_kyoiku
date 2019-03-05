import json
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

import genanki


MAX_GRADE = 6

FORVO_API = 'https://apifree.forvo.com/key/2676e4f71e3649035a68dd8ce3cd8c4e/format/json/language/ja/action/standard-pronunciation/word/'
FORVO_KEY = os.environ.get('FORVO_KEY')


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
        self.recording = None

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
kanji_meanings = {}
tree = ET.parse('data/kanjidic2.xml')
root = tree.getroot()
for entry in root.findall('character'):
    character = entry.find('literal').text

    try:
        entry.find('reading_meaning').find('rmgroup').findall('meaning')
    except AttributeError:
        continue

    meanings = []
    for meaning in entry.find('reading_meaning').find('rmgroup').findall('meaning'):
        # TODO add option to build for different languages
        if 'm_lang' in meaning.attrib:
            continue
        meanings.append(meaning.text)

    kanji_meanings[character] = meanings

    try:
        grade = int(entry.find('misc').find('grade').text)
    except:
        continue
    if grade > MAX_GRADE:
        continue

    for line in open('data/wikipedia-20150422-lemmas.tsv'):
        if character not in line:
            continue
        word = line.split()[-1]
        # make sure we have a dictionary entry for the word before using it
        if word in word_entries:
            break

    kanji = Kanji(character, meanings, grade)
    kanji_list.append(kanji)
    if word not in words:
        words[word] = []
    words[word].append(kanji)

print('getting example word definitions...')

for word in word_entries.values():
    for entry in word:
        try:
            word = entry.find('k_ele').find('keb').text
        except:
            continue

        if word not in words:
            continue

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

        for kanji in words[word]:
            kanji.add_word(Word(word, reading, senses))

grades = [[] for _ in range(MAX_GRADE)]
for kanji in kanji_list:
    grades[kanji.grade - 1].append(kanji)

for grade in grades:
    grade.sort()

decompositions = {}
for line in open('data/kradfile-u'):
    if line.startswith('#'):
        continue
    kanji, decomposition = line.strip().split(' : ')
    decomposition = decomposition.split()
    if kanji in decomposition:
        decomposition.remove(kanji)
    decomposition = ' '.join(decomposition)
    decompositions[kanji] = decomposition

if FORVO_KEY:
    print('downloading recordings...')

    try:
        os.mkdir('media')
    except FileExistsError:
        pass

    api_limit_hit = False
    for grade in grades:
        for kanji in grade:
            if api_limit_hit:
                continue

            if kanji.words:
                word = kanji.words[0].word
            else:
                continue

            filename = os.path.join('media', word+'.mp3')
            if os.path.exists(filename):
                continue

            try:
                print('downloading recording for %s...' % word)
                r = urllib.request.urlopen(
                    FORVO_API + urllib.parse.quote(word)).read()
                data = json.loads(r)
                items = data['items']
                if not items:
                    print('no recording for', word)
                    f = open(filename, 'w')
                    f.close()
                    continue
                mp3_url = items[0]['pathmp3']
                urllib.request.urlretrieve(mp3_url, filename)
            except urllib.error.HTTPError as e:
                print(e)
                api_limit_hit = True

media_files = []
for kanji in kanji_list:
    if kanji.words:
        word = kanji.words[0].word
    else:
        continue

    filename = word+'.mp3'
    if not os.path.exists(os.path.join('media', filename)):
        continue

    kanji.recording = filename
    media_files.append(filename)


print('building Anki package...')

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
        'afmt': '{{FrontSide}}<hr id="answer">{{Meaning}}<br><br><b>{{Example Word}}</b> {{Example Word Recording}}<br>{{Example Word Entry}}<small>{{Decomposition}}</small><br><small>grade {{Grade}}</small>'
    }, {
        'name': 'Word reading',
        'qfmt': '{{#Example Word}}Reading for:<br>{{Example Word}}{{/Example Word}}',
        'afmt': '{{FrontSide}}<hr id="answer">{{Example Word Entry}}<br>{{Example Word Recording}}'
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
            font-size: 12px;
            padding: 1px;
            text-align: left;
        }
        .entry-definition {
            font-size: 10px;
        }
        .entry-other-kanji {
            font-size 10px;
            border: none;
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
            example_entry += '<td><span style="white-space:nowrap;">%s</span></td>' % word.reading
            example_entry += '<td class="entry-definition">%s</td>' % '<br>'.join(
                word.senses)
            example_entry += '</tr>'
        example_entry += '</table><br>'

        other_kanji_table = '<table>'
        for character in example_word:
            if character == kanji.character:
                continue
            if character not in kanji_meanings:
                continue
            other_kanji_table += '<tr><td class="entry-other-kanji">%s</td><td class="entry-other-kanji">%s</td></tr>' % (
                character, ', '.join(kanji_meanings[character]))
        other_kanji_table += '</table>'
        if '<tr>' in other_kanji_table:
            example_entry += other_kanji_table

        if kanji.recording:
            recording = '[sound:%s]' % kanji.recording
        else:
            recording = ''

        note = KanjiNote(
            model=kanji_model,
            fields=[
                kanji.character,
                ', '.join(kanji.meanings),
                example_word,
                example_entry,
                recording,
                decompositions[kanji.character],
                str(kanji.grade),
            ],
        )
        deck.add_note(note)

os.chdir('media')
package = genanki.Package(deck)
package.media_files = media_files
package.write_to_file('../kyoiku.apkg')
