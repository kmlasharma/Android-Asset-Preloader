Readme:
usage: Loader_Utility.py [-h] [-generate_contacts GENERATE_CONTACTS]
                         [-csv CSV] [-push_docs PUSH_DOCS]
                         [-make_docs [NUMBERS [NUMBERS ...]]]
                         [-clean_contacts] [-clean_documents CLEAN_DOCUMENTS]

optional arguments:
  -h, --help            show this help message and exit
  -generate_contacts GENERATE_CONTACTS
                        number of contacts to generate (default 50)
  -csv CSV              a filename.csv file containing all contacts to be read
                        in and created.
  -push_docs PUSH_DOCS  the name of the folder of the files to push to target
                        device
  -make_docs [NUMBERS [NUMBERS ...]]
                        three arguments 1) the amount docs to create 2) the
                        size of each doc 3) the unit of size eg kb, mb
  -clean_contacts       clear all contacts from phone
  -clean_documents CLEAN_DOCUMENTS
                        clean the documents from a given local file path from
                        a phone
Description:
This is a helper script written in python to do the following:
* Permanently install java if it is not already installed.
* Temporarily install ADB if it is not already installed.
* Create and push a specified amount of contacts
* Read in a csv and produce contacts from it.
* Push existing files to a phone.
* Create a specified amount of documents of a specified size and push to a phone.
* Delete all contacts from phone.
* Delete specified folder of files from the phone.

Requirements:
* Python 2.7
* HomeBrew on MacOS
* Android SDK Command line tools (Loader_Utility will download and install if not downloaded)
* Java SDK (Loader_Utility will download and install if not downloaded)

The following files and folders must NOT be tampered/deleted:
* android_app: This folder contains the APK of the contact helper app
* seed_docs: This folder contains the seed documents in order to generate documents of a specified size.
* Loader_Utility.py: This is the script
* wget.py: This is provided locally to prevent pip installments.


== GENERATING CONTACTS ==
Command: python Loader_Utility -generate_contacts 5
Description: The script will invoke the helper app to generate and push the specified amount of contacts to the phone.

== READING IN CSV FILES ==
Command: python Loader_Utility -csv /Users/exampleuser/Documents/CSV/example.csv
Description: The script will push the csv file to the phone, extract and push the contacts, then delete the csv file.
The csv file must:
	* have the first row being the headings: firstname, lastname, [email, note, website], phone - with email, note and website being optional.
	* The label names can be fairly flexible. eg 'first name', 'URL', 'phone no'
	* the text must not overflow the cells, otherwise it will not be correctly extracted.

== PUSHING EXISTING DOCUMENTS ==
Command: python Loader_Utility -push_docs /Users/exampleuser/Documents/DocumentsToPush/
Description: The script will iterate through every file in 'DocumentsToPush' and push them individually to the phone.

== MAKING DOCUMENTS == 
Command: python Loader_Utility -make_docs 20 500 MB
Description: The above command will invoke the script to generate 20 500mb txt documents, using the seeding documents, into an etc folder, and then push them onto the device. Each document is sample latin text.
Units kb, mb and gb are supported.

== DELETING CONTACTS ==
Command: python Loader_Utility -clean_contacts
Description: The above command will delete all contacts from the phone. Note that this command is invoked implicitly by the script before any contact creation.

== DELETING DOCUMENTS FROM THE PHONE ==
Command: python Loader_Utility -clean_documents /Users/exampleuser/Documents/DocumentsToPush/
Description: The above command will check if each document from 'DocumentsToPush' exists on the phone, and will then delete it.





