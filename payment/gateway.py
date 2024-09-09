import uuid

PROMOTION_COST = 500

def mock_payment_gateway(amount):
    if amount == PROMOTION_COST:
        return {'transaction_id': str(uuid.uuid4()), 'success': True}

    return {'transaction_id': None, 'success': False}
