import numpy as np


earth_radius = 6378140.0  # meters
earth_axis_inclination = 23.45  # degrees
seconds_per_day = 86400


def equation_of_time(day):
    "returns the number of minutes to add to mean solar time to get actual solar time."
    b = 2 * np.pi / 364.0 * (day - 81)
    return 9.87 * np.sin(2 * b) - 7.53 * np.cos(b) - 1.5 * np.sin(b)


def get_solar_time(longitude_deg, when):
    "returns solar time in hours for the specified longitude and time," \
    " accurate only to the nearest minute."
    when = when.utctimetuple()
    return \
        (
            (when.tm_hour * 60 + when.tm_min + 4 * longitude_deg + equation_of_time(when.tm_yday))
        /
            60
        )


def get_hour_angle(when, longitude_deg):
    solar_time = get_solar_time(longitude_deg, when)
    return 15 * (12 - solar_time)


def get_declination(day):
    '''The declination of the sun is the angle between
    Earth's equatorial plane and a line between the Earth and the sun.
    The declination of the sun varies between 23.45 degrees and -23.45 degrees,
    hitting zero on the equinoxes and peaking on the solstices.
    '''
    return earth_axis_inclination * np.sin((2 * np.pi / 365.0) * (day - 81))


def get_altitude(latitude_deg, longitude_deg, when):
    day = when.utctimetuple().tm_yday
    declination_rad = np.radians(get_declination(day))
    latitude_rad = np.radians(latitude_deg)
    hour_angle = get_hour_angle(when, longitude_deg)
    first_term = np.cos(latitude_rad) * np.cos(declination_rad) * np.cos(np.radians(hour_angle))
    second_term = np.sin(latitude_rad) * np.sin(declination_rad)
    return np.degrees(np.arcsin(first_term + second_term))


def get_azimuth(latitude_deg, longitude_deg, when):
    day = when.utctimetuple().tm_yday
    declination_rad = np.radians(get_declination(day))
    latitude_rad = np.radians(latitude_deg)
    hour_angle_rad = np.radians(get_hour_angle(when, longitude_deg))
    altitude_rad = np.radians(get_altitude(latitude_deg, longitude_deg, when))
    azimuth_rad = np.arcsin(np.cos(declination_rad) * np.sin(hour_angle_rad) / np.cos(altitude_rad))
    if (np.cos(hour_angle_rad) >= (np.tan(declination_rad) / np.tan(latitude_rad))):
        return np.degrees(azimuth_rad)
    else:
        return (180 - np.degrees(azimuth_rad))


def get_air_mass_ratio(altitude_deg):
    # from Masters, p. 412
    return 1.0 / np.sin(np.radians(altitude_deg))


def get_apparent_extraterrestrial_flux(day):
    # from Masters, p. 412
    return 1160 + (75 * np.sin(2 * np.pi / 365 * (day - 275)))


def get_optical_depth(day):
    # from Masters, p. 412
    return 0.174 + (0.035 * np.sin(2 * np.pi / 365 * (day - 100)))


def get_radiation_direct(when, altitude_deg):
    # from Masters, p. 412
    day = when.utctimetuple().tm_yday
    flux = get_apparent_extraterrestrial_flux(day)
    optical_depth = get_optical_depth(day)
    air_mass_ratio = get_air_mass_ratio(altitude_deg)
    return flux * np.exp(-1 * optical_depth * air_mass_ratio)
