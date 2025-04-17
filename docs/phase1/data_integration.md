# Data Integration

LYIK and TTK systems will constantly exchange data and there needs to be fixed protocol and API endpoints to exchange data. The following are the envisaged integration points

## Token Exchange
All LYIK API are protected by LYIK Tokens. Hence its imperative that the TTK system obtain the equivalent token for all operations. Tokens have to be obtained for all types of users as certain operations are allowed by only certain types of users.
For instance users with only `client` and `maker` roles can create a travel record. Only a `back office admin` will be able to modify parts of the record after the record is validated by the `checker`.
### API Endpoint
> TODO: Provide the details of the `/v1/token` endpoint

### TTK Token
The format of the TTK token that will be exchanged for the LYIK Token will be fixed. The token should, at a minimum, contain the following information
1. Digital Identifier (`id`)
	1. This should be the digital identifier, such as mobile number or email address or even a user id, that is used to identify the logged in user uniquely in the system.
	2. The digital identifier is used by the LYIK system to fetch the relevant records.
	3. For example: If the `id` is a mobile number, the only the records that are associated with that mobile number are fetched.
	4. It's strongly suggested that a human actor (be it the client or any TTK employee) be identified by one and only one `id`
	5. This means a client should not be allowed to be identified by both `mobile` and `email`
2. Role
	1. The role of the user that is to be logged into the system
	2. LYIK can recognise the following roles
		1. `client`
		2. `maker`
		3. `parent_maker`
		4. `checker`
		5. `parent_checker`
		6. `bo_admin`

### Format of the TTK Token

> [!NOTE] Attention Baskar
> What is the format of the token ?
> Will the token be encrypted or encoded ?
> Will the token be self contained or should the details be fetched from an API endpoint
> Will the format of the token be similar for `clients` and `TTK Employees`


## Create Travel Record
TTK will create the travel records for each traveller in the LYIK system the very first time. These travel records will contain some very basic information that will enable the `client` to start the visa application digital journey. The `maker` can also assist the client with the journey.

## Fetch Form Meta Information
3. Get the `LYIK form` for a particular visa
    1. The each form is uniquely identified by a URI
    2. The TTK system has to be aware of this URI and get the mapping
    3. The mapping has to be obtained dynamically by the TTK system
        1. NOTE: The URI is system generated
4. Get all the filled `Visa Forms` for a given user
    4. The user could either be a `client` or it could be invoked from the TTK back office !
    5. TTK back office might need to get the details of the status of a particular application form
    6. This is a two step process. The first step is to get the ID of the particular record and then fetch the details for that record