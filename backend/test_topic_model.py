from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

topics = [
    "Roads and Infrastructure",
    "Water Supply",
    "Sanitation and Waste Management",
    "Public Transportation",
    "Electricity and Power Supply",
    "Healthcare Services",
    "Education Services",
    "Public Safety and Street Lighting",
    "Government Services",
    "Environment and Parks"
]
comments = [
    "Nobody has repaired the potholes on our street even after several complaints.",
    "We have not received drinking water for the last four days.",
    "The garbage truck does not come regularly to our neighborhood.",
    "There is only one bus every hour and it is always overcrowded.",
    "Our area experiences power cuts almost every evening.",
    "The government hospital asked us to buy basic medicines outside.",
    "There are not enough teachers in the local government school.",
    "The street lights have been broken for more than two weeks.",
    "I applied for a birth certificate but my application has not been processed.",
    "The lake near our colony has become polluted with plastic and other waste.",
    
    "The road connecting our village to the main highway becomes unusable during rain.",
    "The water coming from the public tap is dirty and unsafe to drink.",
    "The drainage is overflowing and dirty water is entering people's houses.",
    "There is no proper bus service for people living in our village.",
    "The transformer keeps failing and the entire area loses electricity.",
    "Patients at the public hospital have to wait several hours before seeing a doctor.",
    "Our school building needs repairs and there are not enough classrooms.",
    "Women do not feel safe walking through this area at night because there is no lighting.",
    "I have visited the government office three times but my application is still pending.",
    "The park has become a dumping ground and needs to be cleaned."
]

for comment in comments:
    result = classifier(
        comment,
        candidate_labels=topics,
        hypothesis_template="This feedback is about {}."
    )

    print("\nComment:", comment)
    print("Predicted topic:", result["labels"][0])
    print("Confidence:", round(result["scores"][0] * 100, 2), "%")