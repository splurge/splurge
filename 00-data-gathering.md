# Data gathering

All text files are to be in UTF8 format. The current FTP to hold the data is:  ftp://splurge.scholarsportal.info (password-protected; if you need to know, ask).

# Directory Structure

These changes will solve streaming issues we would hit when adding new files to the FTP server.

    splurge.scholarsportal.info/[institution]/[tmp|now_unix_timestamp]/items.txt
    splurge.scholarsportal.info/[institution]/[tmp|now_unix_timestamp]/transactions.txt

* institution is to be in lower case.
* tmp holds partially uploaded files until all files are ready to be under a timestamp.
* now\_unix\_timestamp is your current timestamp in unix format. 

When uploading files to the ftp first create a temporarily folder tmp! After the upload is complete rename the tmp folder to the timestamp. WHY? because if the server starts to process the data before you finished uploading we will have missing records.

* Only new timestamps for your institution grater then the previously processed timestamp will be used to update the database.
* Duplicate records are ignored but frowned upon. 

`FTP/[institution]/[tmp|now_unix_timestamp]/items.txt`

UTF8 tab-delimited file. Fields:

    itemId (integer)
    ISBN   (string)

Sample:

    114784 → 0415972531 (GOOD !!!)
    114784 → 097522980X (GOOD !!!)
    114782 → 0-9752298-0-X            (BAD - drop the bashes)
    114783 → 0415972531|097522980X    (BAD - piped)
    114783 → 04l597253l               (BAD - ISBN using L not 1)
 

* The item ID is whatever ID you want to use to identify a library book. It must match the itemId contained in the transactions file.
* The ISBN is one ISBN, please don't! separated by a | pipe character, instead create a new line with the same itemId. Also please strip all dashes. 

`FTP/[institution]/[tmp|now_unix_timestamp]/transactions.txt`

UTF8 Tab-delimited file. Fields:

    timestamp (integer)
    itemId    (integer)
    userId    (integer)

Sample:

    1222646400  →  114784  →  67890      (GOOD !!!)
    1225756800  →  103828  →  6A7H8B90   (BAD - not an integer)
    1225756800  →  ABC280   →  76543     (BAD - not an integer)
    1225756800.1232  →  62580   →  76543 (BAD - floating point is not integer)

* The timestamp is in Unix time format (i.e. the number of seconds since 1st Jan 1970 UTC). It is used to calculate the day the transaction occurred on.
* The itemId is whatever ID you want to use to identify a library book. It must match the itemId contained in the item file.
* The userId is whatever ID you want to use to identify an individual library user. This value must be an integer and if requiring some redirection use something like XOR to scramble the userId.
* Any userId anonymizing must be consistent across all your data uploads!

