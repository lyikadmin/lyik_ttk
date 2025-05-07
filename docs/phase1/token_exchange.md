# About Access Token

LYIK and TTK systems will constantly exchange data and there needs to be fixed protocol and API endpoints to exchange data. The API endpoints in LYIK are protected by tokens. This document talks about the role of tokens and how the two systems will use them.

## Token Exchange
All LYIK API are protected by LYIK Tokens. Hence its imperative that the TTK system obtain the equivalent token for all operations. Tokens have to be obtained for all types of users as certain operations are allowed by only certain types of users.
For instance users with only `client` and `maker` roles can create a travel record. Only a `back office admin` will be able to modify parts of the record after the record is validated by the `checker`.

```mermaid
sequenceDiagram
	actor cl as Traveller
	participant ttk as TTK Portal
	participant api as LYIK API
	
	cl->>ttk: Mobile + OTP
	ttk-->ttk: Generate a token (TTK-JWT)
    ttk->>api: Obtain LYIK Token
    api-->api: Generate LYIK Token (LYIK-JWT)
    api-->>ttk: Return LYIK-JWT
```
### API Endpoint
The API endpoint to exchange the token is `/v1/auth/get-token`
This endpoint has to be invoked using the HTTP `POST` method.
The details of the API can be obtained using the Swagger docs form the running instance of the LYIK API server

> [!NOTE] Needs a TTK specific token plugin
> Since the platform has to cater to a TTK specific token, a special plugin has to be developed and only then will the endpoint be meaningful. This plugin will be developed by LYIK as part of the product delivery to TTK


### TTK Token
The format of the TTK token that will be exchanged for the LYIK Token will be fixed. The token should, at a minimum, contain the following information
1. Digital Identifier (`user_id`)
	1. This should be the digital identifier, such as mobile number or email address or even a user id, that is used to identify the logged in user uniquely in the system.
	2. The digital identifier is used by the LYIK system to fetch the relevant records.
	3. For example: If the `id` is a mobile number, the only the records that are associated with that mobile number are fetched.
	4. It's strongly suggested that a human actor (be it the client or any TTK employee) be identified by one and only one `id`
	5. This means a client should not be allowed to be identified by both `mobile` and `email`
2. Role (`role`)
	1. The role of the user that is to be logged into the system
	2. LYIK can recognise the following roles
		1. `client`
		2. `maker`
		3. `parent_maker`
		4. `checker`
		5. `parent_checker`
		6. `bo_admin`
3. Name (`display_name`)
	1. This is the name of the user
	2. This will be used for display purpose only
4. Expiry Time (`expiry_time`)
	1. The time at which the token will be marked for expiry
5. Governed users (`governed_users`)
	1. If the logged in user is a `maker` or a `checker` then there is a possibility of permitting the logged in user to view the work (records) or other makers or checkers
	2. This is the `user_id` of the users whose record can be view by the logged in user

### Format of the TTK Token
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIxMDAiLCJmdWxsTmFtZSI6Ikpob24gRG9lIiwiYWNjZXNzVHlwZSI6Im1ha2VyIiwibG9naW5UaW1lIjoiMjAyNS0wNC0yNSAxNToxMDozMCIsImV4cGlyeVRpbWUiOiIyMDI1LTA0LTI1IDE2OjEwOjMwIn0.5PB_bnlbY40pKW50cPWX7w2ZZk9iQCg_R1e3yc7q
```

The following are the characteristics of the token
1. The token will be a `JWT` 
2. The token will be signed using symmetric key
3. The key will be made available for verification through an environment variable

### Format of the LYIK Token
LYIK token will a signed JWT. The TTK portal will not have to interpret the token at any time.
The LYIK token will contain the TTK Token embedded in it. The embedded TTK Token will be used by LYIK API to invoke the TTK API whenever needed.
#### How to handle expired tokens
Currently the LYIK portal checks for the expiry of tokens and takes appropriate action, such as prompting the user to relogin. But now since the login is happening through the TTK portal, a similar function should be executed in the TTK portal. If the LYIK token is expired, then the TTK portal should fetch a new token and then continue with the subsequent operation of opening the form portal

