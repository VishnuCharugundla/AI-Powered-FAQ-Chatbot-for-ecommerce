import pandas as pd
from azure.storage.blob import BlobServiceClient
from io import StringIO
from openai import AzureOpenAI
from fuzzywuzzy import fuzz, process
from config import Settings

# Load FAQ from Blob
def load_faq_data():
    blob_service_client = BlobServiceClient.from_connection_string(Settings.BLOB_CONN_STR)
    container_client = blob_service_client.get_container_client(Settings.BLOB_CONTAINER)
    blob_client = container_client.get_blob_client(Settings.BLOB_FILE)

    blob_data = blob_client.download_blob().readall()
    csv_string = blob_data.decode("utf-8")
    df = pd.read_csv(StringIO(csv_string))
    return df

# Match FAQ
def find_best_faq_answer(user_question, df, threshold=80):
    questions = df['question'].tolist()
    best_match, score = process.extractOne(user_question, questions, scorer=fuzz.token_sort_ratio)

    if score >= threshold:
        answer = df[df['question'] == best_match]['answer'].values[0]
        return answer
    else:
        return None

# GPT fallback
def get_gpt_answer(user_question):
    client = AzureOpenAI(
        api_key=Settings.OPENAI_KEY,
        api_version="2023-07-01-preview",
        azure_endpoint=Settings.OPENAI_ENDPOINT
    )

    system_prompt = (
        "You are a helpful e-commerce assistant. Answer customer queries clearly and concisely "
        "based on general store policies."
    )

    response = client.chat.completions.create(
        model=Settings.OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        temperature=0.7,
        max_tokens=200
    )

    return response.choices[0].message.content.strip()
