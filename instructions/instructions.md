- This is a full stack project to manage data flow.
- It is written mostly in python.
- Always used a modular, reproducible and easy to maintain approach using classes. Refactor code as needed.
- Always annotate the code for a human to understand what the logic is and what the technical decisions were.

# tools
## backend tools
- mongoDB
- fastapi
## frontend tools
- react JS
## data tools
- data tools are to be managed in the utils/ folder
- pydantic
- pydantic ai
- google genai

# data flow
## original data
- data will be extracted from several sources
    - google spreadsheets
    - pdf files
- the pdf files will be converted to markdown, processed and merged
## data extraction
- data will be extracted from the google spreadsheets and the markdown files
- it will be structured and validated using pydantic models
- pydantic ai will be used to help extract structured and validated data from natural language texts
## data storage
- the extracted data will be stored in JSON format
- the JSON files will be validated and stored in a mongoDB