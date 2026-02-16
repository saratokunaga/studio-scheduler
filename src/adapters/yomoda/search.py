def search(
    parsed,
    date=None,
    time=None,
    period=None
):

    result = []

    for row in parsed:

        if date and row["date"] != date:
            continue

        if time and row["time"] != time:
            continue

        if period and row["period"] != period:
            continue

        result.append(row)

    return result
