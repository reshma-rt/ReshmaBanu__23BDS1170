import os
from dotenv import load_dotenv
from ibm_watson_machine_learning.foundation_models import Model

load_dotenv()

model_id = os.getenv("MODEL_ID", "ibm/granite-3-3-8b-instruct")

wml_credentials = {
    "url": f"https://{os.getenv('WATSONX_REGION')}.ml.cloud.ibm.com",
    "apikey": os.getenv("WATSONX_API_KEY")
}

project_id = os.getenv("WATSONX_PROJECT_ID")

# Initialize Granite model
model = Model(
    model_id = model_id,
    params={"decoding_method": "greedy", "max_new_tokens": 300},
    credentials=wml_credentials,
    project_id=project_id
)

def get_answer_from_query(vector_store, query):
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
    relevant_docs = retriever.get_relevant_documents(query)

    context = "\n".join([doc.page_content for doc in relevant_docs])
    prompt = f"""Answer the question based on the context below:

Context:
{context}

Question: {query}
Answer:"""

    response = model.generate(prompt=prompt)
    return response['results'][0]['generated_text']
