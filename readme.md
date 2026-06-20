Setup (install)
    
create python venv, then
    
    pip install requirement.txt
    
Then in the same directory, setup playwright

    playwright install

Create .env

And add gemini's api key

GOOGLE_API_KEY=...

Running

(Change the target URL at the top)

    python main.py

JSON schema:

    {
        category_name: [
            {
                "product name": "",
                "SKU": "",
                "price": "",
                "unit": "",
                "availability": "",
                "description": "",
                "specifications": "",
                "alternative products": "",
                "manufacturer": "",
                "category hierarchy": [],
                "product URL": "",
                "image url": ""
            },
            ...
        ]
    }

Have a simple test.log to record bugs

Notes about the project:

Unable to retrieve SKU, because the playwright wouldn't load them apparently?
Please see full_page-after.png
I spent some time trying to fix it, but failed.

In the failed-pagination.py, 
I have an almost working pagination traversal version of main.py. 
Right now, playwright can see the "next page" button, and the HTML is being loading (confirmed by count = 1)
But for some reason, it can not be clicked. 
I have spent a long while thinking about why, but couldn't figure out. 
For now, the main.py does NOT have a working pagination feature yet.

Currently, main.py only accepts 3 items per category, because of limited available tokens during testing.

---

Architect overview:

1. Use playwright to scrap DOM 

(playwright because beautiful soup can't handle dynamic loading, and DOM because the entire HTML/raw text is too much for LLM to handle)

2. Feed DOM to navigator agent to get the specific classnames 

(these class names might change, and probably should not be hard-coded)

3. Use the classname to find and parse for category 

4. For each category, get all the display items using classname 

5. For each item, load its corresponding page

6. Manually select easily available information like image and product url

7. Scrap the text and feed into extract agent to get the rest of the details

8. Save the outputs as JSON file

---

More work needs to be done:

Aside from the SKU and pagination,

Resumability and checkpoints are really important, especially when the tokens are limited

The current implementation of saving as one big JSON is not the best

CSV where we can save each entry directly is probably a better choice (check point wise)
