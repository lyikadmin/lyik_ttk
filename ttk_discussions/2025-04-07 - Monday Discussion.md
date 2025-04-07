
## Meeting Information

**Meeting Date/Time:** 2025-04-07 / 10:30 AM
**Meeting Purpose:** meeting_purpose  
**Meeting Location:** TTK Office, Marathahalli 
**Note Taker:** Akhil Babu

## Attendees

- Deepak K
- Suveer N
- Akhil Babu
- Bhaskar
- Vishnu

## Agenda Items

1. Set the necessary user experience and functionality across the three portals.
	1. Address the main stakeholders in the entire journey
	2. Talk about the 3 stakeholders in 3 portal areas
2. Get the Details so no surprises in Future.
	1. Get clarifications on what should be done
3. Project plan for retail deliverable
4. Discuss Soft Launch

## Discussion Items

#### 1. Stakeholders

1. **Client** = Traveller
2. **Maker** = TTK Employee who fills the form
3. **Checker** = TTK Employee who validates data

	Maker and Checker is the 4 eyes system.
	- Maker has edit, file upload permissions for the form.
	- Maker, Client, currently cannot override the others input. (This can be changed based on weight)
	- Checker cannot edit the form.
	- Maker can see all the records of clients, see the states of the records, and decide who to help complete he form.
	- Checker will go through the submitted form, make sure the data is correct, and then allow it to go through the next steps of the flow

#### 2. Client Journeys:
1. DIY Journey
2. Assisted Journey

	Both will have the same port

#### 3. Portals
1. TTK Portal
2. Form filling Portal used for client.
3. Maker checker portal (for internal team)

#### 4. Retail and Corporate
1. Retail 
	1. Upfront payment
	2. Actors: Ttk, Client
	3. Use Payment gateway to get to lyik form filling
2. Corporate:
	1. Post payment
	2. Actors: Employee, Employer
	3. Domain based login
3. Aspects:
	1. Checklist
	2. Timeline
	3. Application Form
	4. Letters
		1. Invitation Letter
		2. Cover Letter
		3. Templatised for company, country


#### 5. Domain
1. ttkvisas.in = TTK portal
2. ttkvisas.in/visaforms = LYIK Portal (Example path for all lyik endpoints in ui)

#### 6. Sequence 
1. In Clients Perspective:
	1. Pay for service
	2. They provide information (From to country, mobile, visa type)
	3. They reach lyik portal with the records initialized
	4. Lyik Portal shows all travellers in the order. (One order, three travellers).
2. Internal to System:
	1. Take information
	2. Exchange token (TTK Platform requests lyik token using ttk token)
	3. Get Lyik Token
	4. TTK platform requests initialization of records using the token (information is provided here)
		1. From and To Country
		2. Mobile number of the primary contact
		3. Visa Type
	5. UI goes to lyik Portal

#### 7. Checklist 
1. B2C:
	- Its Function of (from_country, to_country, visa_type)
2. B2B:
	- Its Function of (business, from_country, to_country, visa_type)

	**Checklist Definition**
	- Overall Checklist is a superset of data
		- Checklist for a customer is subset of these data is relevant for a customer, based on rules
		- Superset also allows unlimited additional attachments specific to client
	- Ruleset need to be documented. (from SME)
	- Based on these rules, the checklist items may be hidden, to create subset
	- Planning Ruleset documentation for Phase 2

	**Additional attachments specific to Client**
		- Array To Cover Case Specific documents.
		- Take three attributes for each attachment
			- Title
			- Description
			- File Attachment

#### 7. Terms
1. Good To File = SUBMIT
	1. Allowed for both Client and Maker.

#### 8. User Experience Discussion
1. Arrive to TTK portal
2. Login
3. Make Payment, Create New Order
4. New Order goes to Lyik Portal
5. The Lyik Portal Will not have the header or footer of TTK Portal
	1. Lyik Portal will have its own header with TTK design, logo and "Go to Dashboard" button.
	2. Lyik Portal will have no logout button, or any header links from TTK.
	3. Lyik Portal will have "Go to Dashboard" button, to go back to TTK Portal
6. Maker/Client will duplicate documents across the order, if the same document is relevant for co-travellers.

	**Addons:**
		1. Courier, Travel/Document pickup, Insurance, ticket, hotel account, photo dev charges.
		2. We will have this in a single location, at the bottom. 
		3. The addon selections can be across sections, but the consolidated view of all selected addons are in a single section.
		4. User cannot uncheck anything from this addon section.

#### 9. Addon and Payments
1. Client selects the addons in Lyik Portal.
2. Lyik Portal Accepts payment for each traveller separately.
3. Payment Gateway integration (Razorpay)


### General:
1. Freeze the Form in next meeting
2. Have indication of who the traveller is on the UI