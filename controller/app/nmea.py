# Parse NMEA sentences received from GPS
#
# NMEA sentence elements
#
#   sentence is a complete NMEA sentence eg $
#   body     is the payload portion of a sentence
#   checksum the last 2 characters (hex digits) following the "*" separator
#   sentence_type  is the first element in the payload
#   args     a list of arguments that follow the command
#
# Example
#
#  sentence $PMTK314,1,1,1,1,1,5,0,0,0,0,0,0,0,0,0,0,0,0,0*2C
#  body     PMTK314,1,1,1,1,1,5,0,0,0,0,0,0,0,0,0,0,0,0,0
#  checksum 2C
#  sentence_type  PMTK314
#  args     1,1,1,1,1,5,0,0,0,0,0,0,0,0,0,0,0,0,0
#
# Sample messages
#
# $GPRMC,235316.000,A,4003.9040,N,10512.5792,W,0.09,144.75,141112,,*19
# $GPGGA,235317.000,4003.9039,N,10512.5793,W,1,08,1.6,1577.9,M,-20.7,M,,0000*5E
# $GPGSA,A,3,22,18,21,06,03,09,24,15,,,,,2.5,1.6,1.9*3E
#
# Details on message types https://aprs.gids.nl/nmea/

# TODO: use time.mktime to construct unix timestamps
import time

# from datetime import datetime
# from datetime import timezone

SENTENCE_TYPES = {
    'GPGGA': [
        'time_utc',
        'latitude_deg_min',
        'latitude_hemisphere',
        'longitude_deg_min',
        'longitude_hemisphere',
        'fix_quality',
        'satellites',
        'horizontal_dilution',
        'altitude_m',
        'altitude_unit',
        'height_geoid',
        'height_geoid_unit',
        'time_since_last_update',
        'station_id'
    ],
    'GPRMC': [
        'time_utc',
        'status',
        'latitude_deg_min',
        'latitude_hemisphere',
        'longitude_deg_min',
        'longitude_hemisphere',
        'speed_knots',
        'track_angle_deg',
        'date_utc',
        'magnetic_variation',
        'variation_E_W',
    ]
}


def parse_int(nmea_data):
    result = None
    try:
        result = int(nmea_data)
    except ValueError:
        pass
    finally:
        return result


def parse_float(nmea_data):
    result = None
    try:
        result = float(nmea_data)
    except ValueError:
        pass
    finally:
        return result


def parse_degrees(nmea_data):
    """
    Parse a NMEA lat/long data value 'dddmm.mmmm' into a pure degrees value.
    Where ddd is the degrees, mm.mmmm is the minutes.

    :param nmea_data:
    :return: float
    """
    raw = parse_float(nmea_data)
    if raw is None:
        return None
    deg = raw // 100
    minutes = raw % 100
    return round(deg + minutes/60, 6)


def parse_time(nmea_data):
    raw = int(parse_float(nmea_data))
    hour = raw // 10000
    minute = (raw // 100) % 100
    second = raw % 100

    return hour, minute, second


def parse_date(nmea_data):
    day = parse_int(nmea_data[0:2])
    month = parse_int(nmea_data[2:4])
    year = parse_int(nmea_data[4:6])  # NB: 2 digit year
    year = year + 2000 if year else year

    return year, month, day


def parse_lat_lon(nmea_degrees, hemisphere):
    """
    parse a latitude or longitude value as 2 fields - degrees/minutes as 'dddmm.mmmm' and the hemisphere
    which one of 'N','S', 'E' or 'W'
    :param nmea_degrees:
    :param hemisphere:
    :return: float
    """
    degrees = parse_degrees(nmea_degrees)
    if hemisphere.lower() in ('s', 'w'):
        degrees = degrees * -1.0
    return degrees


def split_sentence(sentence):
    """
    Split an NMEA sentence into body and checksum.  Strip off whitespace and the leading "$" if present
    The body is the part of the sentence that is used to compute the checksum.
    If there is no checksum then it will be None

    :param sentence: an NMEA string
    :return: (body, checksum)
    """
    sentence = sentence.strip()     # get rid of whitespace
    if sentence.startswith('$'):   # strip off the starting '$' if present
        sentence = sentence[1:]
    parts = sentence.split('*')
    if len(parts) == 2:
        body, checksum = parts
    else:
        body, checksum = sentence, ""
    return body, checksum


def split_body(body):
    """
    Split the sentence body into the sentence_type and a list of arguments.  The body should be a comma-delimited list

    :param body:
    :return: (sentence_type, args)
    """

    parts = body.split(',')      # separate the payload components
    sentence_type = parts[0] if parts else None
    args = parts[1:]

    return sentence_type, args


def compute_checksum(body):
    """
    Compute the checksum for a sentence body as a string with uppercase hex digits

    :param body:
    :return: checksum string
    """
    checksum = 0
    for char in body:
        checksum ^= ord(char)
    return '{:02X}'.format(checksum)


def create_sentence(body):
    """
    Construct a sentence from a sentence body
    This will compute and append a checksum and prepend a '$'
    :param body:
    :return:
    """
    checksum = compute_checksum(body)
    return '${}*{}'.format(body, checksum)


def parse_sentence(sentence):
    result = {
        'sentence': sentence
    }
    body, checksum = split_sentence(sentence)
    if checksum.upper() != compute_checksum(body):
        result['error'] = 'Invalid checksum'
        return result

    sentence_type, args = split_body(body)
    result['sentence_type'] = sentence_type

    if sentence_type in SENTENCE_TYPES:
        fields = SENTENCE_TYPES[sentence_type]
    else:
        fields = ['field{}'.format(i) for i in range(1, len(args) + 1)]

    if len(args) < len(fields):
        result['error'] = 'Expected {} parameters for {} but got {}'.format(len(fields), sentence_type, len(args))
        return result

    args = dict(zip(fields, args))

    if sentence_type == 'GPGGA':
        args = parse_gpgga_args(args)
    elif sentence_type == 'GPRMC':
        args = parse_gprmc_args(args)

    result.update(args)

    return result


def parse_gpgga_args(args):
    # Parse the arguments  for NMEA GPGGA 3D location fix sentence.

    return dict(
        time_utc=parse_time(args['time_utc']),
        latitude=parse_lat_lon(args['latitude_deg_min'], args['latitude_hemisphere']),
        longitude=parse_lat_lon(args['longitude_deg_min'], args['longitude_hemisphere']),
        fix_quality=parse_int(args['fix_quality']),
        satellites=parse_int(args['satellites']),
        horizontal_dilution=parse_float(args['horizontal_dilution']),
        altitude_m=parse_float(args['altitude_m']),
        height_geoid=parse_float(args['height_geoid'])
    )


def parse_gprmc_args(args):
    # Parse the arguments for NMEA GPRMC minimum location fix sentence.

    result = dict(
        time_utc=parse_time(args['time_utc']),
        status=args['status'],
        fix_quality=1 if args['status'].upper() == 'A' else 0,
        latitude=parse_lat_lon(args['latitude_deg_min'], args['latitude_hemisphere']),
        longitude=parse_lat_lon(args['longitude_deg_min'], args['longitude_hemisphere']),
        speed_knots=parse_float(args['speed_knots']),
        track_angle_deg=parse_float(args['track_angle_deg']),
        date=parse_date(args['date_utc'])
    )
    hour, minute, second = result['time_utc']
    year, month, day = result['date']

    t = (year, month, day, hour, minute, second, 0, 0, 0)
    result['utc_seconds'] = int(time.mktime(t))
    return result
