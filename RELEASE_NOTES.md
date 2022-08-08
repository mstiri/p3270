
# v0.1.4
- Add new methods: `sendHome()`, `sendKeys(keys)`  and `delWord()`

## What's Changed
* Add send keys to send severals chars by @DaniloToroL in https://github.com/mstiri/p3270/pull/13

## New Contributors
* @DaniloToroL made their first contribution in https://github.com/mstiri/p3270/pull/13

**Full Changelog**: https://github.com/mstiri/p3270/compare/v0.1.3...v0.1.4

# v0.1.3
- When initialized the client, it is now using charset as intended (http://x3270.bgp.nu/Unix/s3270-man.html#Character-Sets)
- Added new function to ReadTextAtPosition
- Encoding and decoding is set up dynamically from the given codePage, according to http://x3270.bgp.nu/Unix/s3270-man.html#Character-Sets. Only handles western charsets but should be easily extended if needed.
- Decoder will strip away \r.
- Added trySendTextToField - it will go to the field given in coordinates, clear the field, and type in the text given. It will then check what was written and return true if what is written in the field matches the text.
- Added waitForField - will wait for the field to be ready where the cursor is.
- Added foundTextAtPosition, will look at a given position and return true if the text requested is found, false if not.
- Added readTextArea - takes 4 parameters; coordinates for row and column, as well as a length for both columns and rows to read. If more than one row is read, it will return a list of strings split on newline.
