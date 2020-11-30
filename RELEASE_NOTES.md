
version 0.1.3

- When initialized the client, it is now using charset as intended (http://x3270.bgp.nu/Unix/s3270-man.html#Character-Sets)
- Added new function to ReadTextAtPosition
- Decoder now uses latin1 to decode, and will strip away \r.
