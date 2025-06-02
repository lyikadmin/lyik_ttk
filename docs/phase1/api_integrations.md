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

#### LYIK -> TKK
1. Addons API
	1. Get the list of Addons, their cost, etc
2. Get earliest available appointments
	1. Get a set of earliest available appointment for given from, to country, and current date etc.
3. Get Appointment List to change appointment date
	1. For a customer preference, fetch 3 dates and locations, to let them change the appointment preference
4. 