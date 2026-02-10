"""
Payment service for handling mobile payments across African networks.
Supports: M-Pesa, MTN Money, Airtel Money, Flutterwave, Stripe, PayPal
"""

import logging
from decimal import Decimal
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import os
import requests

logger = logging.getLogger(__name__)


class PaymentProcessor:
    """Base class for payment processors"""
    
    def __init__(self):
        self.provider_name = "base"
    
    def initiate_payment(self, phone_number: str, amount: Decimal, currency: str, 
                        subscription_tier: str) -> Tuple[bool, str, Optional[str]]:
        """
        Initiate payment.
        Returns: (success, message, transaction_id)
        """
        raise NotImplementedError
    
    def verify_payment(self, transaction_id: str) -> Tuple[bool, Dict]:
        """
        Verify payment status.
        Returns: (success, payment_details)
        """
        raise NotImplementedError
    
    def refund(self, transaction_id: str) -> Tuple[bool, str]:
        """
        Process refund for a transaction.
        Returns: (success, message)
        """
        raise NotImplementedError


class MPesaPaymentProcessor(PaymentProcessor):
    """M-Pesa payment processor for Kenya"""
    
    def __init__(self):
        super().__init__()
        self.provider_name = "mpesa"
        self.api_key = os.getenv('MPESA_API_KEY')
        self.business_shortcode = os.getenv('MPESA_SHORTCODE', '174379')
        self.passkey = os.getenv('MPESA_PASSKEY')
        self.callback_url = os.getenv('MPESA_CALLBACK_URL')
        self.api_url = "https://api.safaricom.co.ke/mpesa"  # Production
        
        if os.getenv('DEBUG'):
            self.api_url = "https://sandbox.safaricom.co.ke/mpesa"  # Sandbox
    
    def initiate_payment(self, phone_number: str, amount: Decimal, currency: str,
                        subscription_tier: str) -> Tuple[bool, str, Optional[str]]:
        """
        Initiate M-Pesa STK push payment.
        Phone number should be in format: 254XXXXXXXXX (with country code)
        """
        try:
            # Convert amount to KES if needed
            if currency != 'KES':
                # Simple conversion (in production, use real exchange rate API)
                amount_in_kes = int(amount * Decimal('130'))  # Approximate USD to KES
            else:
                amount_in_kes = int(amount)
            
            # Generate timestamp and password
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = self._generate_password(timestamp)
            
            payload = {
                'BusinessShortCode': self.business_shortcode,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': amount_in_kes,
                'PartyA': phone_number,
                'PartyB': self.business_shortcode,
                'PhoneNumber': phone_number,
                'CallBackURL': self.callback_url,
                'AccountReference': f"BRILLIANT_{subscription_tier}",
                'TransactionDesc': f"BrilliantAfrica {subscription_tier} subscription",
            }
            
            headers = self._get_headers()
            response = requests.post(
                f"{self.api_url}/stkpush/v1/processrequest",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            result = response.json()
            
            if result.get('ResponseCode') == '0':
                transaction_id = result.get('CheckoutRequestID')
                message = "M-Pesa prompt sent to your phone. Enter PIN to confirm."
                return True, message, transaction_id
            else:
                message = result.get('ResponseDescription', 'M-Pesa payment initiation failed')
                return False, message, None
                
        except Exception as e:
            logger.error(f"M-Pesa payment error: {str(e)}")
            return False, "Payment service temporarily unavailable. Please try again.", None
    
    def verify_payment(self, transaction_id: str) -> Tuple[bool, Dict]:
        """Check payment status using CheckoutRequestID"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = self._generate_password(timestamp)
            
            payload = {
                'BusinessShortCode': self.business_shortcode,
                'Password': password,
                'Timestamp': timestamp,
                'CheckoutRequestID': transaction_id,
            }
            
            headers = self._get_headers()
            response = requests.post(
                f"{self.api_url}/stkpushquery/v1/query",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            result = response.json()
            payment_details = {
                'transaction_id': transaction_id,
                'status': 'completed' if result.get('ResultCode') == '0' else 'failed',
                'response_code': result.get('ResultCode'),
                'mpesa_receipt': result.get('MpesaReceiptNumber'),
            }
            
            return result.get('ResultCode') == '0', payment_details
            
        except Exception as e:
            logger.error(f"M-Pesa verification error: {str(e)}")
            return False, {'error': str(e)}
    
    def refund(self, transaction_id: str) -> Tuple[bool, str]:
        """Process M-Pesa refund"""
        # Implementation depends on M-Pesa reversal/refund API
        return False, "M-Pesa refunds require manual processing"
    
    def _get_headers(self) -> Dict:
        """Get authorization headers"""
        return {
            'Authorization': f'Bearer {self._get_access_token()}',
            'Content-Type': 'application/json',
        }
    
    def _get_access_token(self) -> str:
        """Get M-Pesa OAuth token"""
        # In production, implement proper OAuth flow
        return os.getenv('MPESA_ACCESS_TOKEN', 'demo_token')
    
    def _generate_password(self, timestamp: str) -> str:
        """Generate M-Pesa password for STK push"""
        import base64
        text = f"{self.business_shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(text.encode()).decode()


class MTNMoneyPaymentProcessor(PaymentProcessor):
    """MTN Money payment processor for Uganda, Ghana, Cameroon"""
    
    def __init__(self):
        super().__init__()
        self.provider_name = "mtn"
        self.api_key = os.getenv('MTN_API_KEY')
        self.api_secret = os.getenv('MTN_API_SECRET')
        self.api_url = os.getenv('MTN_API_URL', 'https://api.mtn.com/v1')
    
    def initiate_payment(self, phone_number: str, amount: Decimal, currency: str,
                        subscription_tier: str) -> Tuple[bool, str, Optional[str]]:
        """Initiate MTN Mobile Money payment"""
        try:
            # MTN requires specific currency per country
            country_currency = self._get_country_currency(phone_number)
            
            payload = {
                'amount': str(amount),
                'currency': country_currency,
                'externalId': f"BRI_{subscription_tier}_{datetime.now().timestamp()}",
                'payer': {
                    'partyIdType': 'MSISDN',
                    'partyId': phone_number,
                },
                'payerMessage': f"BrilliantAfrica {subscription_tier} subscription",
                'payeeNote': "Educational platform subscription",
            }
            
            headers = {
                'X-Reference-Id': f"BRI_{datetime.now().timestamp()}",
                'Content-Type': 'application/json',
                'Ocp-Apim-Subscription-Key': self.api_key,
            }
            
            response = requests.post(
                f"{self.api_url}/collection/v1_0/requesttopay",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201, 202]:
                transaction_id = response.headers.get('X-Reference-Id')
                return True, "MTN payment request initiated. Check your phone.", transaction_id
            else:
                return False, "MTN payment service error. Please try again.", None
                
        except Exception as e:
            logger.error(f"MTN payment error: {str(e)}")
            return False, "MTN payment service temporarily unavailable.", None
    
    def verify_payment(self, transaction_id: str) -> Tuple[bool, Dict]:
        """Verify MTN payment status"""
        try:
            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key,
            }
            
            response = requests.get(
                f"{self.api_url}/collection/v1_0/requesttopay/{transaction_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                payment_details = {
                    'transaction_id': transaction_id,
                    'status': 'completed' if data.get('status') == 'SUCCESSFUL' else 'pending',
                    'response_status': data.get('status'),
                }
                return data.get('status') == 'SUCCESSFUL', payment_details
            else:
                return False, {'error': 'Payment verification failed'}
                
        except Exception as e:
            logger.error(f"MTN verification error: {str(e)}")
            return False, {'error': str(e)}
    
    def refund(self, transaction_id: str) -> Tuple[bool, str]:
        """Process MTN refund"""
        return False, "MTN refunds require manual approval"
    
    def _get_country_currency(self, phone_number: str) -> str:
        """Determine currency based on phone number prefix"""
        if phone_number.startswith('256'):  # Uganda
            return 'UGX'
        elif phone_number.startswith('233'):  # Ghana
            return 'GHS'
        elif phone_number.startswith('237'):  # Cameroon
            return 'XAF'
        else:
            return 'USD'


class FlutterwavePaymentProcessor(PaymentProcessor):
    """Flutterwave payment processor - supports multiple African countries"""
    
    def __init__(self):
        super().__init__()
        self.provider_name = "flutterwave"
        self.secret_key = os.getenv('FLUTTERWAVE_SECRET_KEY')
        self.api_url = "https://api.flutterwave.com/v3"
    
    def initiate_payment(self, phone_number: str, amount: Decimal, currency: str,
                        subscription_tier: str) -> Tuple[bool, str, Optional[str]]:
        """Initiate Flutterwave payment"""
        try:
            payload = {
                'tx_ref': f"BRI_{datetime.now().timestamp()}",
                'amount': str(amount),
                'currency': currency,
                'customer': {
                    'phone_number': phone_number,
                    'name': f"Student {phone_number}",
                },
                'customizations': {
                    'title': 'BrilliantAfrica',
                    'description': f'{subscription_tier} subscription',
                },
                'meta': {
                    'subscription_tier': subscription_tier,
                },
                'redirect_url': os.getenv('FLUTTERWAVE_CALLBACK_URL'),
            }
            
            headers = {
                'Authorization': f'Bearer {self.secret_key}',
                'Content-Type': 'application/json',
            }
            
            response = requests.post(
                f"{self.api_url}/payments",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            result = response.json()
            
            if result.get('status') == 'success':
                checkout_url = result['data']['link']
                transaction_id = result['data']['id']
                return True, f"Payment link: {checkout_url}", transaction_id
            else:
                return False, result.get('message', 'Payment initiation failed'), None
                
        except Exception as e:
            logger.error(f"Flutterwave payment error: {str(e)}")
            return False, "Payment service error", None
    
    def verify_payment(self, transaction_id: str) -> Tuple[bool, Dict]:
        """Verify Flutterwave payment"""
        try:
            headers = {
                'Authorization': f'Bearer {self.secret_key}',
            }
            
            response = requests.get(
                f"{self.api_url}/transactions/{transaction_id}/verify",
                headers=headers,
                timeout=10
            )
            
            result = response.json()
            
            if result.get('status') == 'success':
                data = result['data']
                payment_details = {
                    'transaction_id': transaction_id,
                    'status': 'completed' if data.get('status') == 'successful' else 'pending',
                    'amount': data.get('amount'),
                    'currency': data.get('currency'),
                }
                return data.get('status') == 'successful', payment_details
            else:
                return False, {'error': 'Payment verification failed'}
                
        except Exception as e:
            logger.error(f"Flutterwave verification error: {str(e)}")
            return False, {'error': str(e)}
    
    def refund(self, transaction_id: str) -> Tuple[bool, str]:
        """Process Flutterwave refund"""
        try:
            headers = {
                'Authorization': f'Bearer {self.secret_key}',
                'Content-Type': 'application/json',
            }
            
            response = requests.post(
                f"{self.api_url}/transactions/{transaction_id}/refund",
                headers=headers,
                timeout=10
            )
            
            result = response.json()
            
            if result.get('status') == 'success':
                return True, "Refund processed successfully"
            else:
                return False, result.get('message', 'Refund failed')
                
        except Exception as e:
            logger.error(f"Flutterwave refund error: {str(e)}")
            return False, f"Refund error: {str(e)}"


class PaymentManager:
    """High-level payment management interface"""
    
    PROCESSORS = {
        'mpesa': MPesaPaymentProcessor,
        'mtn': MTNMoneyPaymentProcessor,
        'airtel': MTNMoneyPaymentProcessor,  # Similar API structure
        'flutterwave': FlutterwavePaymentProcessor,
    }
    
    @staticmethod
    def get_processor(payment_method: str) -> Optional[PaymentProcessor]:
        """Get appropriate payment processor"""
        processor_class = PaymentManager.PROCESSORS.get(payment_method.lower())
        if processor_class:
            return processor_class()
        return None
    
    @staticmethod
    def recommend_payment_method(phone_number: str) -> str:
        """Recommend best payment method based on phone number prefix"""
        if phone_number.startswith('254'):  # Kenya
            return 'mpesa'
        elif phone_number.startswith('256'):  # Uganda
            return 'mtn'
        elif phone_number.startswith('233'):  # Ghana
            return 'mtn'
        elif phone_number.startswith('234'):  # Nigeria
            return 'flutterwave'
        else:
            return 'flutterwave'  # Fallback to Flutterwave


# Subscription tier pricing in different currencies
PRICING = {
    'basic': {'USD': 5, 'KES': 650, 'UGX': 18500, 'GHS': 30, 'NGN': 2500},
    'premium': {'USD': 10, 'KES': 1300, 'UGX': 37000, 'GHS': 60, 'NGN': 5000},
    'school': {'USD': 20, 'KES': 2600, 'UGX': 74000, 'GHS': 120, 'NGN': 10000},
}


def get_subscription_price(tier: str, currency: str = 'USD') -> Optional[Decimal]:
    """Get price for a subscription tier in a specific currency"""
    if tier in PRICING and currency in PRICING[tier]:
        return Decimal(str(PRICING[tier][currency]))
    return None
