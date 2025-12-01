#1.  SPECIFIC: (Hrni) To schengen? Is this specific to schengen or not? lot of checks for checkbox, more info box, etc. (Hrni)
from .additional_travel_details_verifier.additional_travel_details_verifier import AdditionalTravelDetailsVerifier
#2.  Universalized
from .passport_verifier.verifier import PassportVerificationPlugin
#3.  Universalized
from .passport_verifier.passport_ip_verifier import PassportIPVerifier
#4.  SPECIFIC: (Hrni) To schengen?  is previous visas same?
from .previous_visas_verifier.previous_visas_verifier import PreviousVisasVerifier
#5.  Universalized 
from .visa_request_summary_verifier.visa_request_summary_verifier import VisaRequestVerifier
#6.  Universalized  
from .appointment_details_verifier.appointment_verifier import AppointmentDetailsVerifier
#7.  Universalized   
from .submit_application_verifier.submit_application_verifier import SumbitApplicationVerifier
#8.  Universalized 
from .financial_verifiers.financial_verifiers import SalarySlipVerifier
#9.  Universalized 
from .financial_verifiers.financial_verifiers import BankStatementVerifier
#10. Universalized 
from .financial_verifiers.financial_verifiers import ITRAcknowledgeVerifier
#11. SPECIFIC: (Hrni) To schengen?
from .travel_insurance_verifier.travel_insurance_verifier import TravelInsuranceVerifier
#12. Universalized 
from .cover_letter_verifier.cover_letter_verifier import CoverLetterVerifier
#13. Universalized  
from .invitation_letter_verifier.invitation_letter_verifier import InvitationLetterVerifier
#14. Universalized
from .appointment_api_verifier.appointment_api_verifier import AppointmentAPIVerifier
#15. SPECIFIC: (Hrni) Some Countries does not have additional documents? Why is that? (Saudi)
from .additional_documents.additional_documents_traveller_verifier import AdditionalDocumentsTravellerVerifier
#16. SPECIFIC: (Hrni) Some Countries does not have comments section? Why is that? (Singapore)
from .comments.comments_verifier import CommentsVerifier
#17. Universalized
from .notification.notification_verifier import NotificationVerifier