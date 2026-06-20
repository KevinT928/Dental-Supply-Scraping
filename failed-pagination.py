import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

from navigatorAgent import navAgent
from detailExtractorAgent import extractAgent
import logging
import json
import time

url = "https://www.safcodental.com/catalog/gloves"
# url = "https://www.safcodental.com/catalog/sutures-surgical-products"

logging.basicConfig(
    filename='test.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

async def get_dom_structure(page):
    js_code = """
    (function getStructure(node) {
        if (!node || node.nodeType !== 1) return null; // Only process element nodes
        
        let obj = {
            tag: node.tagName.toLowerCase(),
            class: node.className || "",
            children: []
        };
        
        for (let child of node.children) {
            let childObj = getStructure(child);
            if (childObj) {
                obj.children.push(childObj);
            }
        }
        
        return obj;
    })(document.body)
    """

    return await page.evaluate(js_code)

async def main():
    logging.info("The application started successfully.")

    async with async_playwright() as p:
        try: 
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")
            logging.info(f"page loaded successfully: {url}")

            # dom_map = await get_dom_structure(page)
            # logging.info("DOM loaded successfully")

            # navResponse = navAgent(json.dumps(dom_map))
            # logging.info("Navigation Agent response: ", navResponse)

            # start_index = navResponse.find("{")
            # end_index = navResponse.rfind("}")
            # if (start_index == -1 or end_index == -1):
            #     logging.warning("Can not parse Navigation Agent's JSON response")
            #     return
            
            # print("Parsed response: ", navResponse[start_index: end_index+1])
            # navResponseJson = json.loads(navResponse[start_index: end_index+1])

            # cate_class_name = navResponseJson["Category class name"]
            cate_class_name = "ais-HierarchicalMenu-item"
            # item_class_name = navResponseJson["Product class name"]
            item_class_name = "ais-Hits-item"

            print("cate_class_name: ", cate_class_name)
            print("item_class_name: ", item_class_name)

            categories = await page.locator("." + cate_class_name + " a").all_inner_texts()
            category_names = [item.split("\n")[0] for item in categories]
            logging.info(f"Categories retrieved: {category_names}")

            all_items = {}

            for name in category_names[1:4]:
                print("--------------------------------------------")
                print(f"starting to process category: {name}")
                logging.info("--------------------------------------------")
                logging.info(f"starting to process category: {name}")

                filter_button = page.locator("." + cate_class_name + " a", has_text=name)

                category_items = []
                has_content = True

                while has_content:
                    await filter_button.click()
                    await page.wait_for_load_state("networkidle")
                    await page.wait_for_timeout(500) 

                    after_display_items = await page.locator("." + item_class_name + " a").all()
                    
                    item_links = [await item.get_attribute("href") for item in after_display_items]
                    print(item_links)

                    logging.info(f"Category items for the page loaded successfully: {name}")

                    for product_link in item_links[:1]:
                        print("---------")
                        print(f"Processing category {name}'s item: {product_link}")
                        logging.info("---------")
                        logging.info(f"Processing category {name}'s item: {product_link}")

                        item_page = await browser.new_page()
                        await item_page.goto(product_link, wait_until="networkidle")
                        logging.info(f"product page loaded successfully: {product_link}")

                        hierarchy = item_page.locator("div.top-container ol li")
                        hierarchy = await hierarchy.all_inner_texts()
                        hierarchy = [a.replace("/", "").strip() for a in hierarchy]
                        # print(hierarchy)

                        # manufacturer = page.locator('div.product-info-main a[href*="shop-by-manufacturer"]')
                        manufacturer = item_page.locator('a[href*="shop-by-manufacturer"]')
                        manufacturer = await manufacturer.all_inner_texts()
                        manufacturer = [a.strip() for a in manufacturer]
                        # print(manufacturer[2])

                        # Tried to get the SKU and product name... But failed
                        # prod_name = item_page.locator(".group-container")
                        # group_locator = item_page.locator(".group-container")
                        # group_texts = await group_locator.all_inner_texts()
                        # print(group_texts)

                        # await item_page.screenshot(path="full_page-before.png", full_page=True)
                        # await item_page.wait_for_selector(".group-container")
                        # await item_page.screenshot(path="full_page-after.png", full_page=True)

                        img_locator = await item_page.locator("#gallery img").first.get_attribute("src")
                        # print(img_locator)

                        # soup = BeautifulSoup(await item_page.content(), "html.parser")
                        # soup_text = soup.get_text(strip=True)
                        # extractResponse = extractAgent(soup_text)
                        # # print(extractResponse)

                        # start_index = extractResponse.find("{")
                        # end_index = extractResponse.rfind("}")
                        # # print(start_index)
                        # # print(end_index)
                        # if (start_index == -1 or end_index == -1):
                        #     logging.warning("Can not parse Extractor Agent's JSON response")
                        #     return
                        
                        # extractResponseJson = json.loads(extractResponse[start_index: end_index+1])
                        extractResponseJson = {}

                        extractResponseJson["manufacturer"] = manufacturer[2]
                        extractResponseJson["category hierarchy"] = hierarchy
                        extractResponseJson["product URL"] = product_link
                        extractResponseJson["image url"] = img_locator

                        print(extractResponseJson)

                        category_items.append(extractResponseJson)

                        # wait for LLM 
                        time.sleep(0.5)
                        print("Item processed successfully")
                        logging.info("Item processed successfully")

                        await item_page.close()

                    print("page processed successfully")
                    logging.info("page processed successfully")

                    print("Pagination ----------------------------- ")
                    pagination = await page.locator(".ais-Stats-text").all_inner_texts()
                    pagination = pagination[0].split(" ")
                    if len(pagination) > 2 and int(pagination[1].split("-")[1]) < int(pagination[3]):
                        print("We need to turn to next page")

                        # next_page = await page.locator(".ais-Pagination-link")
                        filter_button = page.locator(".ais-Pagination-link", has_text="Next page")
                        print(await page.locator(".ais-Pagination-link", has_text="Next page").count())
                    else:
                        has_content = False
                        print("Pagination done")
                
                all_items[name] = category_items
                time.sleep(0.5)

                print("---- Category processed successfully")
                logging.info("---- Category processed successfully")

            print("-------- Done ---------")
            logging.info("-------- Done ---------")

            print(all_items)
            
            with open("data.json", "w") as file:
                json.dump(all_items, file, indent=2)

            await browser.close()

        except Exception as e:
            print("Error: ", e)

asyncio.run(main())






# response = requests.get(url, headers=header)
# if response.status_code == 200:
#     print("all good")
#     soup = BeautifulSoup(response.content, 'lxml')
#     # soup = BeautifulSoup(response.content, 'html.parser')

#     img_count = len(soup.find_all("img"))
#     print("img count: ", img_count)

#     # reduce not needed information, so we can actualy feed into LLM
#     # for tag in soup(["script", "style"]):
#     #     tag.decompose()
    
#     title = soup.find("title")
#     print("title: ", title)

#     meta_desc = soup.find("meta", attrs={"name": "description"})
#     print("meta description: ", meta_desc)


#     # print([t.text for t in soup.find_all('h3')])
#     print(soup.get_text(separator = " ", strip=True))
# else:
#     print("failed")
#     print(response.status_code)