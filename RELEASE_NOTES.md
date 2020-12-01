
version 0.1.3

- When initialized the client, it is now using charset as intended (http://x3270.bgp.nu/Unix/s3270-man.html#Character-Sets)
- Added new function to ReadTextAtPosition
- Encoding and decoding is set up dynamically from the given codePage, according to http://x3270.bgp.nu/Unix/s3270-man.html#Character-Sets. Only handles western charsets but should be easily extended if needed.
- Decoder will strip away \r.
