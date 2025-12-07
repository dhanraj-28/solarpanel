def explain(area, lat, lon):
    if area == 0:
        return f"No solar panels detected at location ({lat}, {lon})."

    return (
        f"Solar panels detected at location ({lat}, {lon}). "
        f"Estimated total panel area: {area:.2f} square units."
    )
