import base64
import urllib.parse
import codecs

def decode_text(encoded_text):
    try:
        # Try base64 decoding
        decoded_text = base64.b64decode(encoded_text).decode('utf-8')
        return decoded_text
    except base64.binascii.Error:
        pass

    try:
        # Try ROT13 decoding
        decoded_text = codecs.decode(encoded_text, 'rot_13')
        return decoded_text
    except AttributeError:
        pass

    try:
        # Try URL decoding
        decoded_text = urllib.parse.unquote(encoded_text)
        return decoded_text
    except AttributeError:
        pass

    # Add more decoding methods as needed

    # If none of the decoding methods worked
    return None

# Example usage
encoded_text = "DLzRkmEBS6dcjqem4ihgKJVw56WVmckF5pKSNUZ7=eyJpdiI6IjBTYVI1ejVrdFdpSTlCNjVjcEs4Tmc9PSIsInZhbHVlIjoiUmFEYlo0d3hOVTAzVlpBM0c5Y0lDYytTUDhycTQvUHhHMFlMWktxZ3pOTngrVHhTd2hIdzBhMW1TZzBlbWRpellXVW9mMG9PNWU4WHEwbEl4anREZk1RTlJPN2NZK0tkMzBzQ28zaTRUbTVxV3c0czlaWjQza2RndVU3L2l0QVdBeUhLV0tRT2duV2hhY25ndndOMGluNVB1cE1QV1Zza1JFWW5xdlJrN0tVbHB0Qk8rZlg4Wmh2dkVCQ0Z0RkFQb0ZtN3dldTZ5S25NSXpLNHU0R3gxb2ZtTTJCYVo1U0M3OU1BcGRiQ2dOR0YzSzRoRXhCRm9PM2U2WTNlOUNsd2dxSG9ENzBNZjk0ejZLa3lFUXptV0R0NUVqOFZXY2FxQnoweEZ3SzdLcXhKWGU5TllUZHU5RWNteE1hYlhaNnk3OGpITzJLWWE0KzRqRXl4RHRQUVJOS3lDRDhkYWtZVXFabzNSZTVkc2MxVzc2VHQ5cXVyeDVXSEJsektlMk9ETis0bi82TG94OVlEVVhVbFhocGFhM1I5NGRUNS9PdnpyWTZhVTJTUzBHVT0iLCJtYWMiOiI1NDRjOWMyMGM4ZjljOTkwODMxMzkxN2QzYTFjNjZhZTcwNzlmNzcwZTA1YjRjM2QyY2RkOGZmNjkxNjI0MzcyIiwidGFnIjoiIn0%3D"  # Base64 encoded "Hello World!"
decoded_text = decode_text(encoded_text)
if decoded_text is not None:
    print(decoded_text)
else:
    print("Decoding failed.")
