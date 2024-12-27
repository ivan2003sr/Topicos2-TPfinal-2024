ML_PREFIX = "ML"


class Faker:
    "Class that anonimyzes data."

    sites: dict[str, str] = {
        "argenprop": "site1",
        "mercadolibre": "site2",
        "zonaprop": "site3",
    }

    @classmethod
    def anonymize(cls, row: dict) -> dict:
        """Anonimyzes the data in a row."""
        row = row.copy()

        if row.get("listing_id", None):
            row["listing_id"] = cls.id(row["listing_id"])

        row["site"] = cls.site(row["site"])
        row["url"] = None

        return row

    @classmethod
    def site(cls, site: str) -> str:
        "Anonimyzes a site."
        return cls.sites[site.lower()]

    @classmethod
    def id(cls, id: str) -> str | None:
        "Anoniymyzes an id."
        return id[2:] if id.startswith(ML_PREFIX) else id
