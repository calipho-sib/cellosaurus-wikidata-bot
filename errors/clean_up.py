from pathlib import Path

HERE = Path(__file__).parent.resolve()

not_in_path = HERE.joinpath("diseases_not_in_wikidata.txt")

not_in = "\n".join(list(set(not_in_path.read_text().split())))

not_in_path.write_text(not_in)

multiple_path = HERE.joinpath("diseases_with_multiple_matches_in_wikidata.txt")

multiple = "\n".join(list(set(multiple_path.read_text().split())))

multiple_path.write_text(multiple)
