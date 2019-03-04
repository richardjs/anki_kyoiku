This script generates an Anki package for learning the rough meanings of kanji,
ordered by grade level as specified by the Japanese Ministry of Education. By
default, it generates cards for kanji through grade six (known as the kyoiku
kanji). However, it can modified to use any kanji contained in the KANJIDIC
project.

Each Anki flashcard has the kanji on the front side, and its rough meaning, an
example Japanese word using the kanji, and grade level on the back.

# Usage

Install the required packages:

    pip install -r requirements.txt

Then run the script:

    python anki_kyoiku.py

The generated file will be at `kyoiku.apkg`, ready for import into Anki.

# Recordings

The script can download recordings for example words from
[Forvo](https://forvo.com/). To do so, the environment variable FORVO_KEY must
be set to your [Forvo API](https://api.forvo.com/) key. After setting that, run
the script.

Chances are you will hit your daily Forvo API limit before all the recordings
are downloaded. In that case, run the script after your limit resets. The script
will pick up downloads where it left off. You can reimport the deck into Anki
after each wave of downloads, and it should include the new files as expected.

# Data sources

This project makes use of the KANJIDIC and JMdict-EDICT projects, both property
of the Electronic Dictionary Research and Development Group. The projects are
used in conformance with the EDRDG's license, available at
[http://www.edrdg.org/edrdg/licence.html](http://www.edrdg.org/edrdg/licence.html).

This project makes use of the file kradfile-u, created by Jim Rose. It is used
in comformance with its license, available at
[http://www.kanjicafe.com/kradfile_license.htm](http://www.kanjicafe.com/kradfile_license.htm).

This project also makes use of a Japanese frequency list from
[Wiktionary](https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Japanese2015_10000),
available via the [Create Commons Attribution-ShareAlike
License](https://creativecommons.org/licenses/by-sa/3.0/). The TSV version of
the file used in this project can be downloaded at
[http://namakajiri.net/data/wikipedia-20150422-lemmas.tsv](http://namakajiri.net/data/wikipedia-20150422-lemmas.tsv).

All data sources are unmodified.
