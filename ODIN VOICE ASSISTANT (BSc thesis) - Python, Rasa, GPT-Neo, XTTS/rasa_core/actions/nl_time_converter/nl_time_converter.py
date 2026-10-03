import re
from datetime import datetime, timedelta

number_word_mapping = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20, "twenty one": 21, "twenty two": 22,
    "twenty three": 23, "twenty four": 24, "twenty five": 25,
    "twenty six": 26, "twenty seven": 27, "twenty eight": 28,
    "twenty nine": 29, "thirty": 30, "thirty one": 31, "thirty two": 32,
    "thirty three": 33, "thirty four": 34, "thirty five": 35,
    "thirty six": 36, "thirty seven": 37, "thirty eight": 38,
    "thirty nine": 39, "forty": 40, "forty one": 41, "forty two": 42,
    "forty three": 43, "forty four": 44, "forty five": 45,
    "forty six": 46, "forty seven": 47, "forty eight": 48,
    "forty nine": 49, "fifty": 50, "fifty one": 51, "fifty two": 52,
    "fifty three": 53, "fifty four": 54, "fifty five": 55,
    "fifty six": 56, "fifty seven": 57, "fifty eight": 58, "fifty nine": 59
}

expressions = [
    "today", "tomorrow", "tomorrow night", "Saturday night", "tomorrow at two PM"
                                                             "tonight", "next week", "this morning", "tomorrow morning",
    "at ten PM"
    "the day after tomorrow", "two hours from now", "ten hours from now",
    "two days from now", "next Sunday", "in one minute"]

# Standalone words
standalone_pattern = re.compile(
    r'(?i)\b(?P<standalone>today|tonight|tomorrow|morning|afternoon|evening|midnight|noon|the day after tomorrow|night)\b')

# Time specific patterns (at 10 AM, at 5:00, at 6 PM)
specific_pattern = re.compile(
    r'(?i)\bat\s(?P<hour>one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d{1,2})'
    r'(?::(?P<minute>one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d{2}))?\s*'
    r'(?P<ampm>AM|PM)?\b'
)

# Offset patterns (in/after 2 days/one week/one year (from now))
offset_pattern = re.compile(
    r'(?i)\b(in|after)\s+(?P<quantity>one|two|three|four|five|six|seven|eight|nine|ten|'
    r'eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|'
    r'twenty(?:[ -]?one|[ -]?two|[ -]?three|[ -]?four|[ -]?five|[ -]?six|[ -]?seven|[ -]?eight|[ -]?nine)?|'
    r'thirty(?:[ -]?one|[ -]?two|[ -]?three|[ -]?four|[ -]?five|[ -]?six|[ -]?seven|[ -]?eight|[ -]?nine)?|'
    r'forty(?:[ -]?one|[ -]?two|[ -]?three|[ -]?four|[ -]?five|[ -]?six|[ -]?seven|[ -]?eight|[ -]?nine)?|'
    r'fifty(?:[ -]?one|[ -]?two|[ -]?three|[ -]?four|[ -]?five|[ -]?six|[ -]?seven|[ -]?eight|[ -]?nine)?|'
    r'\d+)\s+'
    r'(?P<unit>seconds?|minutes?|hours?|days?|weeks?|months?|years?)\s*'
    r'(from now)?\b'
)

# Next pattern (next week/monday/friday)
next_pattern = re.compile(r'(?i)\bnext\s(?P<next_unit>week|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b')


def parse_time_expression(expression, debug=True):
    print(f'Expression {expression}') 

    # Time variables to be extracted
    specific_hour = None
    offset_second = None
    offset_minute = None
    offset_hour = None
    offset_day = None
    offset_week = None

    # Standalone pattern
    for standalone_match in standalone_pattern.finditer(
            expression):  # finditer because there can be multiple stanalone pattern words in a single expression
        match_group = standalone_match.group('standalone')
        print(f'Standalone match: {match_group}') 

        # A specific case for each standalone pattern
        match match_group:
            case 'tonight':
                specific_hour = 21
            case 'tomorrow':
                offset_day = 1
            case 'night':
                specific_hour = 21
            case 'morning':
                specific_hour = 9
            case 'afternoon':
                specific_hour = 15
            case 'evening':
                specific_hour = 18
            case 'midnight':
                specific_hour = 0
            case 'noon':
                specific_hour = 12
            case 'the day after tomorrow':
                offset_day = 2

        print(f'Specific hour: {specific_hour or -1}') 
        print(f'Offset hour: {offset_hour or -1}') 
        print(f'Offset day: {offset_day or -1}') 
        print(f'Offset week: {offset_week or -1}') 

    # Specific pattern
    if specific_match := specific_pattern.search(expression):
        hour = specific_match.group('hour')
        print(f'Specific match: Hour:{hour}') 

        # Extract/convert the hour
        if hour.isnumeric():
            hour = int(hour)
        else:
            hour = number_word_mapping[hour.lower()]

            # Increment if necessary
        ampm = specific_match.group('ampm') or "AM"
        if ampm.lower() == "pm":
            hour += 12
        specific_hour = hour

        print(f'Specific hour: {specific_hour or -1}') 
        print(f'Offset hour: {offset_hour or -1}') 
        print(f'Offset day: {offset_day or -1}') 
        print(f'Offset week: {offset_week or -1}') 

    # Offset pattern
    if offset_match := offset_pattern.search(expression):
        quantity = offset_match.group('quantity')
        unit = offset_match.group('unit').rstrip('s')
        print(f"Offset match: Quantity: {quantity}, Unit: {unit}") 

        # Extract/convert the quanitity
        if quantity.isnumeric():
            quantity = int(quantity)
        else:
            quantity = number_word_mapping[quantity.lower()]

        # Assign quantity to each the correct unit
        match unit:
            case 'second':
                offset_second = quantity
            case 'minute':
                offset_minute = quantity
            case 'hour':
                offset_hour = quantity
            case 'day':
                offset_day = quantity
            case 'week':
                offset_week = quantity

        print(f'Specific hour: {specific_hour or -1}') 
        print(f'Offset hour: {offset_hour or -1}') 
        print(f'Offset minute: {offset_minute or -1}') 
        print(f'Offset day: {offset_day or -1}') 
        print(f'Offset week: {offset_week or -1}') 

    # Next pattern
    if next_match := next_pattern.search(expression):
        next_unit = next_match.group('next_unit').lower()
        print(f"Next match: Unit: {next_unit}") 

        current_weekday = datetime.today().weekday()

        if next_unit == 'week':
            # Set offset to 7 days for the next week
            offset_day = 7
        else:
            # Calculate the day difference for the next specific day of the week
            target_weekday = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].index(
                next_unit)
            # Days until the next occurrence of the target day
            days_until_next = (target_weekday - current_weekday + 7) % 7
            if days_until_next == 0:
                days_until_next = 7  # If it's today, we want next week's day
            offset_day = days_until_next

        print(f'Specific hour: {specific_hour or -1}') 
        print(f'Offset hour: {offset_hour or -1}') 
        print(f'Offset day: {offset_day or -1}') 
        print(f'Offset week: {offset_week or -1}') 

    now = datetime.now()
    print(f'Now: {now}') 

    # Increment/set new time
    if specific_hour:
        now = now.replace(hour=specific_hour)
    elif offset_hour:
        now += timedelta(hours=offset_hour)
    if offset_second:
        now += timedelta(seconds=offset_second)
    if offset_minute:
        now += timedelta(minutes=offset_minute)
    if offset_day:
        now += timedelta(days=offset_day)
    if offset_week:
        now += timedelta(weeks=offset_week)

    print(f'Then: {now}') 
    print('') 
    return now


def format_datetime(dt):
    def ordinal(n):
        return "%d%s" % (n, "th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))

    day = ordinal(dt.day)
    month = dt.strftime("%B")  # Full month name
    year = dt.year
    hour = dt.strftime("%I")  # 12-hour format
    minute = dt.strftime(":%M") if dt.minute != 0 else ""  # Omit minutes if "00"
    am_pm = dt.strftime("%p")  # AM/PM

    formatted = f"{day} of {month}, {hour}{minute} {am_pm}"
    return formatted


if __name__ == "__main__":
    for expression in expressions:
        parse_time_expression(expression)
