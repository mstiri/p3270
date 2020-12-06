
version 0.1.3

- When initialized the client, it is now using charset as intended (http://x3270.bgp.nu/Unix/s3270-man.html#Character-Sets)
- Added new function to ReadTextAtPosition
- Encoding and decoding is set up dynamically from the given codePage, according to http://x3270.bgp.nu/Unix/s3270-man.html#Character-Sets. Only handles western charsets but should be easily extended if needed.
- Decoder will strip away \r.
- Added clearField functionality. Will always clear the current field where it is stanging, so you have to call moveTo first.
- Added trySendTextToField - it will go to the field given in coordinates, clear the field, and type in the text given. It will then check what was written and return true if what is written in the field matches the text.
- Added waitForField - also depends on where you are standing I suppose.