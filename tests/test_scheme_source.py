from pathlib import Path

from integrations.external.scheme_source import SchemeSourceCSV


def test_scheme_source_csv_maps_expected_columns(tmp_path: Path) -> None:
    csv_path = tmp_path / "schemes.csv"
    csv_path.write_text(
        (
            "scheme_name,slug,details,benefits,eligibility,application,documents,level,schemeCategory,tags\n"
            "Test Scheme,test-scheme,Some details,Some benefits,Age 18-30,Apply online,Aadhaar,Central,Education,student\n"
        ),
        encoding="utf-8",
    )

    source = SchemeSourceCSV(str(csv_path))
    schemes = source.load_schemes()

    assert len(schemes) == 1
    assert schemes[0]["scheme_name"] == "Test Scheme"
    assert schemes[0]["application_process"] == "Apply online"
    assert schemes[0]["documents_required"] == "Aadhaar"
