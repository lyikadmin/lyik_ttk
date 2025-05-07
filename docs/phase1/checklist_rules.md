# Checklist Data Validation Rules
First lets familiarise ourselves with some terms which are very specific to TTK
#### Checklist
A list is a list of documents that are required for processing the visa. The checklist may vary based on the country and the type of visa. A checklist is make up of `data` and `rules`. `Data` is the data that has to be submitted as part of the checklist. Examples are `Passport`, `Insurance`, `Proof of Income` and so on. `Rules` are the business rules that have to be applied on top of the `data` to validate the `data`. These rules are mostly known to the SMEs in TTK.
#### Checklist item
A `checklist item` is actually one piece of information related to a specific `data`. For instance `Passport`. Now for the same passport there could be two checklist items and these items may just vary in the data validation rules that have to be applied on the passport.

The following are the checklist items and the associated rules

## Passport
Some countries need the passport to be valid for 6 months while some other countries need it to be valid for a year.
The validation rule will check this for the passport against the auto extracted 
## VFS Appointment Date Validator
The `client` may want to change the travel dates and other such detail from the `Travel Info` section. When there is any change in data, the LYIK platform will invoke a TTK API to check the the validity of the data.
NOTES:
1. A validation rule in the `Travel Info` section which will internally invoke a TTK API to check the following
	1. How many business days are required to process this visa
	2. What is the last date to file the application ?
	3. Appointment scheduled should be prior to the last date to file the application
    4. This will be a `verifier` plugin in the LYIK system that will internally invoke the TTK API
## Travel Insurance
1. The insurance data has to be validated against the traveller details
2. The `maker` will manually enter the insurance data
	1. In the future phase of the project the data can be automatically read and the data auto filled
3. The system will perform the necessary data checks. The following are the data checks that needs to be performed
	1. TODO: The rules have to be documented
## Travel Itinerary
This checklist rule will be valid only when the client has entered the entire travel itinerary manually in the portal. The portal will provide means to enter the travel itinerary in the form of a table.
1. Travel itinerary rules
    1. The port of entry as per the itinerary has to match the ones for which the Visa is applied for
    2. No dangling dates. If there is one the system should provide a warning

## Previous Visa
One of the checklist items is getting the previous visa information and taking decisions based on that data. The portal will provide means to add previous visa documents. The user can upload any number documents.
While the `client` will just upload the documents, the `maker` will make the necessary entries in the form manually.
NOTE: In a future phase of the project, the information from Visa can be auto extracted and filled in the form.
The following are the checklist rules for this section
1. TODO: Document all the rules
## Proof of Income
The `proof of income` checklist item collects the necessary information from the traveller in the form of `salary statements`, `bank statement`, `ITR returns`.
The `client` will be able to upload the documents and also indicate what type of document is uploaded.
The `maker` can manually fill the data form the uploaded documents.

NOTE: In a future phase of the project the data can be auto extracted and filled in the form

The following are the rules that have to be implemented against the data filled by the `maker`
1. TODO: Document all the rules