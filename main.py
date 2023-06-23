import os
import time
import openai
from dotenv import load_dotenv

load_dotenv("./variables.env")


# determine output file
# version the file based on existing version in the output directory.
def determine_output_file():
    # folder path
    dir_path = "output"
    count = 0
    # Iterate directory
    for path in os.listdir(dir_path):
        # check if current path is a file
        if os.path.isfile(os.path.join(dir_path, path)):
            count += 1
    return "output/v" + str(count + 1) + ".txt"


def write_output(text):
    print(text)
    outPutFile.write(text + "\n\n")


def ask_gpt(text):
    rate_limit_request(text)
    out_text = ""

    # add prompt to conversation
    messages.append({"role": "user", "content": text})

    # Send the request to the API
    completion = openai.ChatCompletion.create(
        model=model_engine,
        messages=messages,
        temperature=0.9,
        max_tokens=4048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        n=1,
        stream=None,
    )

    # Get the corrected text from the response
    out_text = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": out_text})

    # if messages is getting long, remove previous conversations
    if len(messages) > 7:
        messages.pop(2)
        messages.pop(1)

    # Print the corrected text
    write_output(out_text)


# This function is to slow down the number of request to not exceeded the rate limit
def rate_limit_request(text):
    rate_limit = 24000 # tokens per min. actual Limit: 250000.000000
    estimated_tokens = len(text.split(" ")) + len(
        prompt.split(" ")
    )  # * .75 removing to be conservative
    percentage_of_limit_per_min = estimated_tokens / rate_limit
    est_delay_sec = percentage_of_limit_per_min * 60

    print("sleeping for: " + str(est_delay_sec) + " seconds")
    time.sleep(est_delay_sec)


# Chat GPT Set Up
# Set your API key
openai.api_key = os.getenv("OPENAPI_API_KEY")
# Set the model to use (e.g. "gpt-4", "text-davinci-003", "text-davinci-002", "text-curie-001")
model_engine = "gpt-4"

# Set the prompt to use for grammar checking
prompt = os.getenv("PROMPT")

messages = []
messages.append({"role": "system", "content": prompt})

# Open the text file in reading mode
with open("text.txt", "r") as file:
    # Read the contents of the file into a string
    text = file.read()

# Split the string into a list of paragraphs
paragraphs = text.split("\n\n")

outPutFile = open(determine_output_file(), "a")

for text in paragraphs:
    # skip if paragraph doesn't have significant text
    if len(text) < 20:
        write_output(text)
        continue
        # check for a formatted markdown, quote, or citation
    if text.startswith(">") or text.startswith("[^") or text.startswith("#"):
        write_output(text)
        continue
        # check for unformatted bible  citation
    if "bible_text" in text:
        write_output("Found unformatted bible text " + text)
        # send text to gpt
    else:
        ask_gpt(text)


outPutFile.close()
