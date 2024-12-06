from typing import Dict, List, Optional
from datetime import datetime
from uuid import UUID
import docusign_esign as docusign
from docusign_esign import EnvelopesApi, EnvelopeDefinition, Document, Signer, SignHere
from ..core.config import settings

class DocumentTemplate:
    def __init__(self, name: str, content: str, fields: List[str]):
        self.name = name
        self.content = content
        self.fields = fields

class DocumentService:
    def __init__(self):
        self.api_client = docusign.ApiClient()
        self.api_client.host = "https://demo.docusign.net/restapi"  # Use production URL in prod
        self.api_client.set_default_header("Authorization", f"Bearer {settings.DOCUSIGN_API_KEY}")
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> Dict[str, DocumentTemplate]:
        """
        Initialize document templates.
        """
        return {
            "purchase_agreement": DocumentTemplate(
                name="Purchase Agreement",
                content="""
                REAL ESTATE PURCHASE AGREEMENT

                This Agreement is made on {date} between:

                SELLER: {seller_name}
                Address: {seller_address}

                BUYER: {buyer_name}
                Address: {buyer_address}

                1. PROPERTY
                The Seller agrees to sell and the Buyer agrees to buy the property located at:
                {property_address}
                Legal Description: {legal_description}

                2. PURCHASE PRICE
                The purchase price is ${purchase_price} (US Dollars)
                
                3. EARNEST MONEY
                Buyer will deposit ${earnest_money} as earnest money with {escrow_company}

                4. CLOSING
                The closing shall take place on or before {closing_date}

                5. CONTINGENCIES
                This agreement is contingent upon:
                a) Buyer obtaining financing by {financing_date}
                b) Satisfactory home inspection by {inspection_date}
                c) {additional_contingencies}

                6. SIGNATURES

                Seller: ___________________ Date: _________
                
                Buyer: ___________________ Date: _________
                """,
                fields=["date", "seller_name", "seller_address", "buyer_name", "buyer_address",
                       "property_address", "legal_description", "purchase_price", "earnest_money",
                       "escrow_company", "closing_date", "financing_date", "inspection_date",
                       "additional_contingencies"]
            ),
            "listing_agreement": DocumentTemplate(
                name="Listing Agreement",
                content="""
                EXCLUSIVE RIGHT TO SELL LISTING AGREEMENT

                This Agreement is made on {date} between:

                BROKER: {broker_name}
                License #: {broker_license}

                SELLER: {seller_name}
                Address: {seller_address}

                1. PROPERTY
                The Seller grants to the Broker the exclusive right to sell the property at:
                {property_address}

                2. LISTING PRICE
                The property shall be offered for sale at ${listing_price}

                3. COMMISSION
                The Seller agrees to pay the Broker a commission of {commission_rate}%

                4. TERM
                This agreement begins on {start_date} and ends on {end_date}

                5. BROKER'S OBLIGATIONS
                The Broker agrees to:
                {broker_obligations}

                6. SELLER'S OBLIGATIONS
                The Seller agrees to:
                {seller_obligations}

                7. SIGNATURES

                Broker: ___________________ Date: _________
                
                Seller: ___________________ Date: _________
                """,
                fields=["date", "broker_name", "broker_license", "seller_name", "seller_address",
                       "property_address", "listing_price", "commission_rate", "start_date",
                       "end_date", "broker_obligations", "seller_obligations"]
            )
        }

    async def generate_document(self, template_name: str, context: Dict) -> str:
        """
        Generate a document from a template.
        """
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")

        # Validate all required fields are present
        missing_fields = [field for field in template.fields if field not in context]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        # Generate document content
        document_content = template.content.format(**context)
        return document_content

    async def send_for_signature(self, 
                               document_content: str,
                               document_name: str,
                               signers: List[Dict[str, str]]) -> str:
        """
        Send a document for electronic signature using DocuSign.
        """
        try:
            # Create the envelope definition
            envelope_definition = EnvelopeDefinition(
                email_subject="Please sign your real estate document",
                documents=[
                    Document(
                        document_base64=document_content.encode('utf-8'),
                        name=document_name,
                        file_extension="txt",
                        document_id="1"
                    )
                ],
                recipients={"signers": []}
            )

            # Add signers
            for i, signer in enumerate(signers, 1):
                envelope_definition.recipients.signers.append(
                    Signer(
                        email=signer['email'],
                        name=signer['name'],
                        recipient_id=str(i),
                        routing_order=str(i),
                        tabs={
                            "sign_here_tabs": [
                                SignHere(
                                    anchor_string="Signature:",
                                    anchor_units="pixels",
                                    anchor_y_offset="0",
                                    anchor_x_offset="0"
                                )
                            ]
                        }
                    )
                )

            # Create and send the envelope
            envelopes_api = EnvelopesApi(self.api_client)
            results = envelopes_api.create_envelope(
                account_id=settings.DOCUSIGN_ACCOUNT_ID,
                envelope_definition=envelope_definition
            )

            return results.envelope_id

        except Exception as e:
            print(f"Error sending document for signature: {str(e)}")
            raise

    async def get_signature_status(self, envelope_id: str) -> Dict:
        """
        Get the status of a signature request.
        """
        try:
            envelopes_api = EnvelopesApi(self.api_client)
            envelope = envelopes_api.get_envelope(
                account_id=settings.DOCUSIGN_ACCOUNT_ID,
                envelope_id=envelope_id
            )

            return {
                "status": envelope.status,
                "sent_datetime": envelope.sent_datetime,
                "completed_datetime": envelope.completed_datetime,
                "last_modified_datetime": envelope.last_modified_datetime
            }

        except Exception as e:
            print(f"Error getting signature status: {str(e)}")
            raise

    def add_template(self, name: str, content: str, fields: List[str]) -> None:
        """
        Add a new document template.
        """
        self.templates[name] = DocumentTemplate(name, content, fields)

# Create a singleton instance
document_service = DocumentService() 