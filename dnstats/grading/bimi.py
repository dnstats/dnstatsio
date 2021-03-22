from dnstats.dnsvalidate.bimi import Bimi, BimiErrors

def grade(bimis: list, dmarcs: list, domain: str) -> [int, ()]:
    if not bimis:
        return 0, [BimiErrors.N0_BIMI_RECORDS]

    the_bimis = []
    for bimi in bimis:
        if bimi.startswith('v=BIMI1'):
            the_bimis.append(bimi)


    bimi = Bimi(the_bimis, dmarcs)

    if len(bimi.errors) == 0 or bimi.errors == [BimiErrors.SELECTOR_NOT_DEFINED]:
        return 100, bimi.errors
    else:
        return 0, bimi.errors