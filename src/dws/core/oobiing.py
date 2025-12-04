from keri.app import habbing


def get_resolved_oobi(hby: habbing.Habery, pre: str) -> str | None:
    """Gets a resolved OOBI for a given identifier prefix or None if not found."""
    for (oobi,), obr in hby.db.roobi.getItemIter():
        if obr.cid == pre:
            return oobi
    return None
