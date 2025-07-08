#### TTK -> LYIK
1. Get LYIK Token
	1. https://forms-uat.ttkservices.com/api/v1/auth/get-token
	2. to create LYIK Token using TTK Token
2. Get Form Name to URL mapping
	1. https://forms-uat.ttkservices.com/api/v1/mgmt/forms/formdata?form_name=Schengen%20Tourist%20Visa
	2. To Get the form names -> URL mapping.
3. Save Record 
	1. https://forms-uat.ttkservices.com/api/v1/forms/28c5984c9e6380bb45bbbd7b384b7ba52fc82243c0802b834faa45c2?action=SAVE
	2. To SAVE (initiate) a record. Can provide appropriate paylaod to specify if its a primary or co-traveller.
4. Get Link Records with Filters
	1. [https://forms-uat.ttkservices.com/api/v1/forms/linkrecord?filters={"Order ID": "order_example123"}]
	2. Get Link Records, with specified filters
5. Get Specific Form Record (with Record ID)
	1. https://forms-uat.ttkservices.com/api/v1/mgmt/forms/cecec5bb196a2670f451078f166ac7d9d65a5cdc8a2ad0835402f659/557790
	2. Get specific Form record, provided record id.
6. Change/Add owner to a Record
	1. http://localhost:8080/api/v1/mgmt/forms/cecec5bb196a2670f451078f166ac7d9d65a5cdc8a2ad0835402f659%2F557790/{recordid}/owners?record_id=103624&mode=Add
	2. Add, Remove, or Replace owners associated to a record, and associated link record.
7. Update the payment status
	1. This API is yet to be created
	2. TTK will invoke this API to update the payment information for a particular add-on

#### LYIK -> TKK
1. Addons API
	1. Get the list of Addons, their cost, etc
2. Get earliest appointment date, fee and other information. This is needed in the `Visa Request Information` section
	1. This API will be used to populate the following
		1. Visa Processing Duration
		2. Earliest appointment availability
		3. Appointment location
		4. Embassy fee
	2. The input to this API should be
		1. State of province of residence (?)
		2. Departure Date
		3. Visa Processing Type
3. Get Appointment List to change appointment date. This information is needed in the `Appointment Details` section
	1. The input the API will be
		1. Province
		2. Date of travel
		3. Preference of wanting an appointment in a specific region
	2. The output of the API will be used to populate the 3 appointment preferences
4. Messaging API
	1. An API to send and receive messages (through WhatsApp) from the traveller
5. Get the list of `locations` where the visa can be applied based on the traveller's residence state / province 
	2. This is seemingly needed in the `Appointment Details` section
	3. What is the purpose of this ? Can this be a simple JSON, CSV file that is statically uploaded ?
6. 