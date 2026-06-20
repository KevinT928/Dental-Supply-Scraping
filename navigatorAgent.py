from callLLM import callGemini

systemPrompt = """
    You are an intelligent web scraping assistant for a dental website.
    You are looking out for the list of products, and the list of categories.
    Do not look for the category list from the page header.
    Instead, look for the category list within filter-container.
    
    Your task is to look through the JSON DOM, and return the class name to use for efficient scraping.

    Return in a JSON format:
    {
        "Category class name": "change_to_actual_class_name",
        "Product class name": "change_to_actual_product_class_name"
    }
"""

def navAgent(content):
    return callGemini(systemPrompt, content)