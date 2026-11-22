answer_evaluation_dataset = [
    {
        "question": "How many annual leave days do employees receive?",
        "expected_terms": ["20 days"],
        "should_refuse": False
    },
    {
        "question": "How many unused annual leave days can employees carry forward?",
        "expected_terms": ["5 unused"],
        "should_refuse": False
    },
    {
        "question": "How many paid sick days are available?",
        "expected_terms": ["10 paid sick days"],
        "should_refuse": False
    },
    {
        "question": "How quickly must employees report a lost device?",
        "expected_terms": ["immediately"],
        "should_refuse": False
    },
    {
        "question": "What is the company's maternity leave policy?",
        "expected_terms": [],
        "should_refuse": True
    }
]