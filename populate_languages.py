import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Language

# Create the app and the database
app = create_app()
app.app_context().push()

# Define the languages to populate with detailed demographics and history
languages = [
    {
        'name': 'Hausa',
        'demographics': (
            'Hausa is a Chadic language spoken by approximately 50 million people primarily in northern Nigeria and Niger. '
            'It is one of the largest African languages in terms of number of speakers and is a major language of trade and commerce in the region. '
            'Hausa is also used as a lingua franca in parts of West Africa, including Chad and Cameroon. '
            'The language is written in both the Latin alphabet and the Arabic script (Ajami), reflecting its historical interactions with Arabic-speaking cultures.'
        ),
        'history': (
            'Hausa is part of the Afroasiatic language family, specifically within the Chadic branch. '
            'The language has a rich literary tradition that dates back to the 19th century, with notable contributions from scholars and poets. '
            'Hausa has been significantly influenced by Arabic due to the spread of Islam in the region, as well as by English through colonial and post-colonial interactions. '
            'The Hausa people have a long history of trade and cultural exchange, which is reflected in the language’s vocabulary and literary forms.'
        )
    },
    {
        'name': 'Yoruba',
        'demographics': (
            'Yoruba is a Niger-Congo language spoken by about 45 million people in southwestern Nigeria and neighboring countries such as Benin and Togo. '
            'It is one of the largest ethnic languages in Africa and has a significant diaspora in the Americas due to historical migrations and transatlantic slave trade. '
            'The language serves as a major cultural and linguistic identity marker for the Yoruba people and is widely used in media, literature, and education in Nigeria.'
        ),
        'history': (
            'Yoruba belongs to the Volta-Niger branch of the Niger-Congo family. '
            'It has a long history of written literature, with early records dating back to the 19th century. '
            'Yoruba literature includes a wealth of oral traditions, proverbs, and folklore that are integral to Yoruba cultural heritage. '
            'The language has been influenced by various cultural and religious traditions, including Islam and Christianity, which have contributed to its lexicon and literary output.'
        )
    },
    {
        'name': 'Igbo',
        'demographics': (
            'Igbo is a Bantu language spoken by around 44 million people in southeastern Nigeria. '
            'It is one of the major languages of Nigeria and is used in various domains including education, media, and governance. '
            'The Igbo-speaking region is characterized by a rich cultural heritage and a diverse range of dialects, with the standard Igbo language being a central unifying factor for the Igbo people.'
        ),
        'history': (
            'Igbo is part of the Niger-Congo language family, with a wide array of dialects spoken across southeastern Nigeria. '
            'The language has a significant oral literature, including folktales, myths, and proverbs that reflect the cultural values of the Igbo people. '
            'In the 20th century, efforts have been made to standardize and promote Igbo through educational and media institutions, contributing to its preservation and development.'
        )
    },
    {
        'name': 'Fulani',
        'demographics': (
            'Fulani is a West African language spoken by approximately 24 million people across the Sahel region, including countries such as Nigeria, Senegal, and Cameroon. '
            'It is used by the Fulani people, who are a widespread ethnic group in West Africa with a nomadic and pastoral lifestyle. '
            'Fulani serves as a lingua franca in many parts of the Sahel and is used in trade, social interactions, and cultural practices.'
        ),
        'history': (
            'Fulani belongs to the Atlantic branch of the Niger-Congo family. '
            'The language has a rich oral tradition, with a history of epic poetry, proverbs, and storytelling that are central to Fulani culture. '
            'Fulani has been influenced by Arabic due to historical Islamic scholarship and trade, and it is also used in Islamic religious contexts.'
        )
    },
    {
        'name': 'Kanuri',
        'demographics': (
            'Kanuri is a Nilo-Saharan language spoken by about 4 million people in northeastern Nigeria and neighboring countries such as Niger and Chad. '
            'It is the primary language of the Kanuri people and serves as a major means of communication in the region. '
            'Kanuri is used in local administration, education, and media, and it has a significant number of speakers in urban and rural areas.'
        ),
        'history': (
            'Kanuri is part of the Saharan branch of the Nilo-Saharan language family. '
            'The language has a historical significance due to its use in the Kanem-Bornu Empire, a prominent medieval West African state. '
            'Kanuri has a rich literary tradition and has been influenced by Arabic through historical Islamic scholarship and trade.'
        )
    },
    {
        'name': 'Tiv',
        'demographics': (
            'Tiv is a Bantu language spoken by around 3 million people in central Nigeria. '
            'It is used primarily by the Tiv people and serves as a key cultural and linguistic identity for the community. '
            'The language is employed in local governance, education, and media, and it has a significant presence in the central region of Nigeria.'
        ),
        'history': (
            'Tiv belongs to the Niger-Congo family and has a rich tradition of oral literature, including songs, stories, and proverbs. '
            'The language has been used in various cultural and religious contexts and has been influenced by neighboring languages and cultures.'
        )
    },
    {
        'name': 'Idoma',
        'demographics': (
            'Idoma is a Niger-Congo language spoken by about 2 million people in central Nigeria. '
            'It is used by the Idoma people and serves as an important medium of communication in the Idoma-speaking region. '
            'Idoma is utilized in local administration, media, and educational contexts, and it plays a crucial role in maintaining cultural heritage.'
        ),
        'history': (
            'Idoma is part of the Benue-Congo branch of the Niger-Congo family. '
            'The language has a significant oral tradition, with a wealth of proverbs, folktales, and songs that reflect the cultural values of the Idoma people. '
            'Idoma has been influenced by neighboring languages and has evolved through interactions with other ethnic groups in the region.'
        )
    },
    {
        'name': 'Ibibio',
        'demographics': (
            'Ibibio is a Benue-Congo language spoken by approximately 3 million people in southeastern Nigeria. '
            'It is used by the Ibibio people and serves as a major language in the southeastern region. '
            'Ibibio is utilized in local governance, media, and cultural practices, and it plays a central role in the community’s identity.'
        ),
        'history': (
            'Ibibio is part of the Niger-Congo family and has a rich tradition of oral literature, including myths, proverbs, and traditional songs. '
            'The language has been used in various cultural and religious contexts and has a history of interaction with other ethnic groups and languages in southeastern Nigeria.'
        )
    },
    {
        'name': 'Efik',
        'demographics': (
            'Efik is a Benue-Congo language spoken by about 1 million people in southeastern Nigeria. '
            'It is closely related to Ibibio and is used in various domains including local administration, education, and media. '
            'Efik serves as a key cultural and linguistic marker for the Efik people and is used in traditional ceremonies and practices.'
        ),
        'history': (
            'Efik is a closely related language to Ibibio and shares a significant amount of vocabulary and cultural practices with it. '
            'The language has a rich literary tradition and has been used in various historical and cultural contexts, including traditional governance and education.'
        )
    },
    {
        'name': 'Gwari',
        'demographics': (
            'Gwari is a Niger-Congo language spoken by around 2 million people in central Nigeria. '
            'It is used by the Gwari people and serves as an important language in the central region of Nigeria. '
            'Gwari is employed in local governance, education, and media, and it plays a significant role in the cultural identity of its speakers.'
        ),
        'history': (
            'Gwari belongs to the Benue-Congo branch of the Niger-Congo family and has a rich tradition of oral literature. '
            'The language is used in various cultural and social contexts and has been influenced by interactions with neighboring languages and cultures.'
        )
    }
]

# Insert languages into the database
with app.app_context():
    for lang in languages:
        language = Language(
            name=lang['name'],
            demographics=lang['demographics'],
            history=lang['history']
        )
        db.session.add(language)
    db.session.commit()

print("Languages have been added to the database.")
