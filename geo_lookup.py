import geoip2.database

reader = geoip2.database.Reader("geoip/GeoLite2-Country.mmdb")


def get_country_from_ip(ip):
    try:
        response = reader.country(ip)
        return response.country.name or "Unknown"
    except Exception:
        return "Unknown"
