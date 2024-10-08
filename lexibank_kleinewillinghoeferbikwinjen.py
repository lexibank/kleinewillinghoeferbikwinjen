import attr
import csv
import pylexibank
from clldutils.path import Path
from clldutils.misc import slug


@attr.s
class CustomLanguage(pylexibank.Language):
    Source = attr.ib(default=None)
    Region = attr.ib(default=None)


class Dataset(pylexibank.Dataset):
    dir = Path(__file__).parent
    id = "kleinewillinghoeferbikwinjen"
    language_class = CustomLanguage
    writer_options = dict(keep_languages=False, keep_parameters=False)
    form_spec = pylexibank.FormSpec(
        brackets={"(": ")"},
        separators=(";", "/", ",", "~", "("),
        missing_data=("", " "),
        replacements=[(" ?", "")], 
        strip_inside_brackets=True,
    )

    def cmd_makecldf(self, args):
        data = []

        concepts = args.writer.add_concepts(
            id_factory=lambda c: c.id[:24].replace("-", "")
            + "_"
            + c.id.split("-")[-1]
            + "_"
            + slug(c.english),
            lookup_factory="Name",
        )

        languages = args.writer.add_languages(lookup_factory="Name")
        args.writer.add_sources()

        comments = {
            "fɛɛni; tshwɐnì (little thing)": "little thing",
            "tswáni; feenì (very small)": "very small",
            "jì(ì) (=calabash)": "=calabash",
            "wáà (swín (~pots)": "~pots",
            "wuo wo; tá (go)": "go",
            "wowə́, wo (sit down)": "sit down",
            "ɗò kàà déé, wuri ka déé (~up)": "~up",
            "e mí (give me)": "give me",
            "ŋə nuŋ (-sth.)": "-sth.",
        }

        for i in ["Wordlist.tsv", "Pronouns and numbers.tsv"]:
            with open(self.dir.joinpath("raw", i).as_posix(), encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile, delimiter="\t")
                raw_lexemes = []
                if i == "Wordlist.tsv":
                    source = self.conceptlists[0].refs[0]
                else:
                    source = self.conceptlists[1].refs[0]
                for row in reader:
                    row["Source"] = source
                    raw_lexemes.append(row)
            data.extend(raw_lexemes)

        for row in pylexibank.progressbar(data):
            for language, lexeme in row.items():
                if language in languages:
                    args.writer.add_forms_from_value(
                        Language_ID=languages[language],
                        Parameter_ID=concepts[row["English"]],
                        Value=lexeme,
                        Comment=comments[lexeme] if lexeme in comments.keys() else "",
                        Source=row["Source"],
                    )
