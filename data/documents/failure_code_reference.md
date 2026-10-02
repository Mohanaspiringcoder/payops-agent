# UPI Payment Failure Code Reference

## TIMEOUT

### Meaning
The transaction did not receive a successful response within the expected processing window.

### Operational Interpretation
A TIMEOUT indicates that the transaction processing flow did not complete within the expected response window.

The failure code alone does not establish the underlying cause.

### Investigation Guidance
For a TIMEOUT failure, operations teams should examine:

- Transaction timestamp
- Transaction status
- Response time
- Sender bank
- Receiver bank
- Channel
- Related transaction logs

### Important Limitation
TIMEOUT alone must not be interpreted as proof of a network failure, server failure, infrastructure failure, or security incident.

---

## INSUFFICIENT_FUNDS

### Meaning
The transaction could not be completed because the available account balance was insufficient for the requested payment.

### Operational Interpretation
The failure indicates insufficient available funds for the transaction.

### Investigation Guidance
Operations teams can examine:

- Transaction amount
- Transaction status
- Sender bank
- Transaction timestamp

---

## BANK_ERROR

### Meaning
The transaction failed with a bank-related processing error.

### Operational Interpretation
The BANK_ERROR code identifies a bank-related processing failure, but the code alone does not establish the specific underlying technical cause.

### Investigation Guidance
Operations teams should examine:

- Sender bank
- Receiver bank
- Transaction timestamp
- Response time
- Related bank processing logs

---

## TECHNICAL_ERROR

### Meaning
The transaction encountered a technical processing error.

### Operational Interpretation
The TECHNICAL_ERROR code indicates that the transaction could not be completed because of a technical processing error.

The failure code alone does not establish the specific underlying cause.

### Investigation Guidance
Operations teams should examine:

- Transaction timestamp
- Response time
- Sender bank
- Receiver bank
- Related application or processing logs
