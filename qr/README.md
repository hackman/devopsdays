generate.py will generate a single PDF including all Avery 5164 labels.

It has only one command line argument specifing either orga or attendees.

If no argument is provided it will provide usage.

- For orga the expected CSV file is: organizers.csv
- For attendees the CSV file should be: attendees.csv

If the csv file is not found, not accessible or empty, it will error out.


We have a few differences, between the CSV files of attendees and organizers.
- In orga we have first name, last name, email, type
- In attendees we don't have type

We also have a difference between the VCARD data for orga and attendees. The orga team has the type put in TITLE and also the ORG is hardcoded to DevOpsDays, while the attendees have DevOpsDays YEAR and no TITLE.


# Installation
On ubuntu you only need:

 pip3 install qrcode reportlab
