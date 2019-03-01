This script generates an Anki package for learning the rough meanings of kanji,
ordered by grade level as specified by the Japanese Ministry of Education. By
default, it generates cards for kanji through grade six (known as the kyoiku
kanji). However, it can modified to use any kanji contained in the KANJIDIC
project.

Each Anki flashcard has the kanji on the front side, and its rough meaning,
example Japanese words using the kanji, and grade level on the back.

# Usage

Install the required packages:

    pip install -r requirements.txt

Then run the script:

    python anki_kyoiku.py

The generated file will be at `kyoiku.apkg`, ready for import into Anki.

Future versions of this script *should* be able to be re-imported into Anki,
and update the cards without breaking any scheduling information or creating
duplicates.

# Data sources

This project makes use of the KANJIDIC and JMdict-EDICT projects, both property
of the Electronic Dictionary Research and Development Group. The projects are
used in conformance with the EDRDG's license, available at
[http://www.edrdg.org/edrdg/licence.html](http://www.edrdg.org/edrdg/licence.html).
