## 8 July 2025
1. The status update API will send these fields
	1. Order ID (`orderId`)
	2. Completed Sections Count (`completedSection`)
	3. Total Sections Count (`totalSection`)
	4. Traveller ID (`travellerId`)
	5. Maker Confirmation (`makerConfirmation`)
		1. This will be `True` if the maker has checked `I have viewed the Traveller's .....` in the `Submit Application` section
	6. Appointment details (`appointmentDetails`)
		1. This value will be populated with an Object containing the following fields
		2. `location`
		3. `date`
		4. `time_hr`
		5. `time_min`
2. The `visa_mode` should be `E Visa` or `Paper Visa`. Check this with Athira
3. Vijetha had questions regarding usage of LYIK Token
	1. Token usage is confirmed
	2. The TTK token has to be sent in the header and not as payload
4. Clarification on showing only relevant documents in the dashboard
	1. The list in the dashboard should contain only the entries relevant to the OrderID in the TTK token
5. No logout button in the LYIK Portal
6. Link to go to TTK dashboard
7. For payment, the `UDF1` field will contain a base64 encoded JSON document. The JSON document will contain a list of objects. Each object will have the following attributes
	1. `orderId`
	2. `travellerId`
	3. `addonId`
	4. `amount`
