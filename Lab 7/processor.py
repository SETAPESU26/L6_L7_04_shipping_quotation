import json
import math


def calculate_dimensional_weight(dimensions_str):
    """Return dimensional weight in kg for 'LxWxH' (cm), or None if input is invalid."""
    if not isinstance(dimensions_str, str):
        return None

    parts = dimensions_str.lower().split('x')
    if len(parts) != 3:
        return None

    try:
        length, width, height = (float(p) for p in parts)
    except ValueError:
        return None

    # Reject NaN/inf and non-positive dimensions
    if not all(math.isfinite(v) and v > 0 for v in (length, width, height)):
        return None

    result = (length * width * height) / 5000.0
    if not math.isfinite(result):  # overflow on huge values
        return None
    return round(result, 2)


def format_tracking_label(raw_code):
    """Return 'P-000123' style label for codes like 'p123', or None if invalid."""
    if not isinstance(raw_code, str) or len(raw_code) < 2:
        return None

    prefix = raw_code[0]
    if not prefix.isalpha():
        return None

    try:
        tracking_num = int(raw_code[1:])
    except ValueError:
        return None

    if tracking_num < 0:
        return None

    return f"{prefix.upper()}-{tracking_num:06d}"


def parse_package_manifest(json_payload):
    """Return the manifest weight as a float, or None if payload is invalid."""
    if not isinstance(json_payload, (str, bytes, bytearray)):
        return None

    try:
        data = json.loads(json_payload)
    except (ValueError, RecursionError):  # JSONDecodeError is a ValueError
        return None

    if not isinstance(data, dict) or "weight" not in data:
        return None

    weight = data["weight"]
    if isinstance(weight, bool):
        return None

    try:
        weight = float(weight)
    except (TypeError, ValueError, OverflowError):
        return None

    if not math.isfinite(weight) or weight < 0:
        return None
    return weight


def main():
    print("==== Running calculate_dimensional_weight ====")
    dims_input = input("Enter dimensions LxWxH in cm (e.g. 20x30x10): ")
    dim_weight = calculate_dimensional_weight(dims_input)
    if dim_weight is None:
        print("Invalid dimensions. Expected format: LxWxH with positive numbers.")
    else:
        print("Dimensional Weight (kg):", dim_weight)

    print("\n==== Running format_tracking_label ====")
    code_input = input("Enter raw code (e.g. E123): ")
    label = format_tracking_label(code_input)
    if label is None:
        print("Invalid code. Expected a letter followed by a non-negative number.")
    else:
        print("Formatted Label:", label)

    print("\n==== Running parse_package_manifest ====")
    json_input = input('Enter manifest JSON (e.g. {"weight": 12.5}): ')
    weight = parse_package_manifest(json_input)
    if weight is None:
        print("Invalid manifest. Expected JSON object with a non-negative numeric 'weight'.")
    else:
        print("Manifest Weight:", weight)


if __name__ == "__main__":
    main()