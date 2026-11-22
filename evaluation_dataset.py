# Questions based on our three sample policy PDFs.
# expected_source identifies the PDF that should contain the answer.
# expected_terms are key pieces of evidence we expect retrieval to find.

evaluation_dataset = [

    {
        "question": "How many annual leave days do employees receive?",
        "expected_source": "employee_handbook.pdf",
        "expected_terms": ["20 days", "annual leave"]
    },

    {
        "question": "How many unused annual leave days can be carried forward?",
        "expected_source": "employee_handbook.pdf",
        "expected_terms": ["5 unused", "March 31"]
    },

    {
        "question": "How many paid sick days are available?",
        "expected_source": "employee_handbook.pdf",
        "expected_terms": ["10 paid sick days"]
    },

    {
        "question": "How many days per week can employees work remotely?",
        "expected_source": "employee_handbook.pdf",
        "expected_terms": ["2 days per week", "manager approval"]
    },

    {
        "question": "What authentication is required for company email?",
        "expected_source": "it_security_policy.pdf",
        "expected_terms": ["multi-factor authentication", "email"]
    },

    {
        "question": "How quickly must employees report a lost device?",
        "expected_source": "it_security_policy.pdf",
        "expected_terms": ["immediately", "lost or stolen devices"]
    },

    {
        "question": "What is the hotel reimbursement limit per night?",
        "expected_source": "travel_expense_policy.pdf",
        "expected_terms": ["150 currency units", "per night"]
    },

    {
        "question": "What is the domestic daily meal allowance?",
        "expected_source": "travel_expense_policy.pdf",
        "expected_terms": ["45", "domestic"]
    },

    {
        "question": "When must employees submit expense claims?",
        "expected_source": "travel_expense_policy.pdf",
        "expected_terms": ["10 calendar days"]
    },

    {
        "question": "How long does expense reimbursement normally take?",
        "expected_source": "travel_expense_policy.pdf",
        "expected_terms": ["15 business days"]
    }
]