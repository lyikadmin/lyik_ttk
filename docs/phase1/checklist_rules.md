# Checklist Data Validation Rules
First lets familiarise ourselves with some terms which are very specific to TTK
#### Checklist
A list is a list of documents that are required for processing the visa. The checklist may vary based on the country and the type of visa. A checklist is make up of `data` and `rules`. `Data` is the data that has to be submitted as part of the checklist. Examples are `Passport`, `Insurance`, `Proof of Income` and so on. `Rules` are the business rules that have to be applied on top of the `data` to validate the `data`. These rules are mostly known to the SMEs in TTK.
#### Checklist item
A `checklist item` is actually one piece of information related to a specific `data`. For instance `Passport`. Now for the same passport there could be two checklist items and these items may just vary in the data validation rules that have to be applied on the passport.

The following are the checklist items and the associated rules

## Visa Request Information
This page contains preliminary information about the type of Visa being requested for.
#### Who can edit this ?
1. `maker` : Maker can surely edit this section at any point in time
2. `client` : Client can edit this section until the maker takes over. Once the maker takes over the client will not be allowed to edit

#### Rules
1. `Departure Date` : What are the rules for date validation ?
2. `Arrival Date` : What are the rules for date validation ?

>[!important] To Athira / Vishnu
> How does the system know that the embassy fee is updated. Based on this the `checkbox` is shown. The business rule is not clear

#### Call To Action
The user (client or maker) can click on the `Validate` button and that will trigger the following actions
1. It will invoke a TTK API with the following data
	1. Selected Province
	2. Visa Processing Type
	3. Anything else ???
2. The API will return the following data
	1. Earliest Appointment Availability
	2. Appointment Location
	3. Updated Embassy Fee
3. The returned data will be auto populated in the `Visa Request` card

#### API Integration

>[!Important] To Baskar & Suveer
> Get the API details for fetching the earliest appointment available, location and embassy fee, given the province, processing type (and anything else)


## Appointment Details
Details about the Visa Appointment with features to change by `traveller` and `maker`

>[!important] Scheduled Location List (Vishnu / Athira / Suveer)
>Will this data be fetched from an API or from a pre defined List (csv) ?

>[!important] Need clarity on cancelling (Vishnu/Athira)
>If the traveller choses to cancel an appointment, how will the system know that the appointment is cancelled ?
>Wouldn't it be simple if the traveller asks for assistance from TTK in case of cancellation / rescheduling

>[!Note] Suggestion 
> Don't have the option of cancelling. As a traveller if I have booked an appointment 


#### Call To Action
Use clicks on `Get available details`. Internally an API is invoked to get the `Locations` and `Date of Appointment`

#### API Integration

>[!important] To Baskar & Suveer
>Get the API to get the Suggested Locations and Date of Appointment. For this the API will be given order_id, state/province and the traveller selected option for Appointment Preference

## Passport
This infopane captures all passport details. All fields are manually editable. The fields are autofilled only for convenience.
#### Rules
1. Some countries need the passport to be valid for 6 months while some other countries need it to be valid for a year
2. If its an Indian passport, then `Issued by` field should always be `Regional Passport Office`
3. `Civil/Marital Status` can have the value `Others`. If the value is `Others` then there should be a Text box that the user can manually fill

>[!Note] For LYIK Engineering Team
>There should not be two cards. All the data has to be consolidated into a single card

>[!important] Passport Validity (Athira/Vishnu)
>What are the rules to check passport validity

## Photograph
There will be multiple `Photograph` sections. Each infopane will be for a set of countries.

>[!Note] For LYIK Engineering Team
>We will have a hidden field which will indicate if the photo is paid for already. If so the `checkbox` to opt for add on service is disabled

## Address
This will capture the address information.
If the `same as permanent address` is chosen, the entire `current residential address` is made non-editable (and not hidden).
Upon saving the address from passport is copied into the `residential address` fields.

>[!Note] For LYIK Engineering Team
>The address copy is done in a `save processor`

## Itinerary and Accommodation
#### Rules
1. The countries that occur in the itinerary should be one of the schengen states
2. If 

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


## Save Processor
1. The fields `Earliest Appointment Availability` and `Appointment Location` should be copied to the fields in the section `Appointment Details`
	1. This is part of the `Visa Request Information`
2. The entire form for the primary traveller has to be stored for the secondary traveller to fetch information from
	1. The store will be specific to the TTK plugin
3. Store the `short country code` (such as IN) in part of the form that is accessible to all sections
	1. There are sections that are visible only for certain countries
	2. There could be rules based on countries. Hence need this in the form
4. In the `photograph` section, if the add on service is chosen and if the service is paid for, then set the `hidden field` in the photograph section. This will make the add on checkbox non editable
5. In the `Address` infopane, if the `same as passport` is checked, then always copy the passport address into the `residential address` fields.
6. In the `Itinerary And Accommodation` section if the user has chosen `I want TTK to book a dummy....` or `I want TTK to book a confirmed...` the add-on section is updated
	1. If the hotel booking is already done, then the options are non-editable

## New Field Types
1. Create a new field type which will allow only Schengen countries to be entered