# Checklist Data Validation Rules
First lets familiarise ourselves with some terms which are very specific to TTK
#### Checklist
A list is a list of documents that are required for processing the visa. The checklist may vary based on the country and the type of visa. A checklist is make up of `data` and `rules`. `Data` is the data that has to be submitted as part of the checklist. Examples are `Passport`, `Insurance`, `Proof of Income` and so on. `Rules` are the business rules that have to be applied on top of the `data` to validate the `data`. These rules are mostly known to the SMEs in TTK.
#### Checklist item
A `checklist item` is actually one piece of information related to a specific `data`. For instance `Passport`. Now for the same passport there could be two checklist items and these items may just vary in the data validation rules that have to be applied on the passport.

The following are the checklist items and the associated rules

## Passport

>TODO: make a list of data that needs to be captured from the passport.
>Also identify the types of files (PDF, JPEG, PNG etc) that the client may provide from the passport details are to be extracted

Some countries need the passport to be valid for 6 months while some other countries need it to be valid for a year
## VFS Appointment Date Validator
1. Check appointment date and other date changes
    2. When the travel dates are changed by the `client` or the `maker` , the TTK system has to be invoked to check and obtain the new appointment dates etc
    3. This will be a `verifier` plugin in the LYIK system that will internally invoke the TTK API
## Travel Insurance
> TODO: Get the sample documents from the top insurance providers

1. The insurance data has to be validated against the traveller details

## Travel Itinerary
1. Travel itinerary rules
    1. The port of entry as per the itinerary has to match the ones for which the Visa is applied for
    2. No dangling dates. If there is one the system should provide a warning
## Proof of Income
> TODO : Financial information data and validation